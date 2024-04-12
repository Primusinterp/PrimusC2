import React, { useEffect, useState } from 'react';
import { Box, Heading, Text,Stack ,Select,Button, useDisclosure,Spinner, useToast, Flex, Modal, ModalOverlay, ModalContent, ModalHeader, ModalCloseButton, ModalBody, FormControl, FormLabel, Input } from '@chakra-ui/react';
import { useForm } from 'react-hook-form';
import { useQuery, useMutation, toast } from 'react-query';

async function fetchListenerTypes() {
  const response = await fetch('/api/listener-types');
  if (!response.ok) {
    throw new Error('Network response was not ok');
  }
  return response.json();
}

async function fetchInterfaces() {
  const response = await fetch('/api/interfaces');
  if (!response.ok) {
    throw new Error('Network response was not ok');
  }
  return response.json();
}

async function compileImplant(compileData) {
  const response = await fetch('/api/compile-implant', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(compileData),
  });
  if (!response.ok) {
    throw new Error('Network response was not ok');
  }
  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;

  // Extract the filename from the Content-Disposition header
  const contentDisposition = response.headers.get('Content-Disposition');
  let filename = 'implant.exe'; // Default filename
  if (contentDisposition) {
    const filenameMatch = contentDisposition.match(/filename="?([^"]+)"?/i);
    if (filenameMatch && filenameMatch[1]) {
      filename = filenameMatch[1];
    }
  }

  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
}

async function startListener(listenerData) {
  const response = await fetch('/api/start-listener', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(listenerData),
  });
  if (!response.ok) {
    throw new Error('Network response was not ok');
  }
  return response.json();
}

function ListenerList({ fetchListeners }) {
  const [listeners, setListeners] = useState([]);
  const killModal = useDisclosure();
  const [compilingListenerId, setCompilingListenerId] = useState(null); 

 

  useEffect(() => {
    fetchListeners().then(setListeners);
  }, [fetchListeners]);

  const handleCompile = async (listener) => {
    try {
      setCompilingListenerId(listener.ID); 
      await compileImplant(listener);
      setCompilingListenerId(null); 
  
      
      toast({
        title: "Implant compiled",
        description: "The implant has been successfully compiled.",
        status: "success",
        duration: 9000,
        isClosable: true,
      });
    } catch (error) {
      setCompilingListenerId(null); 
      console.error('An error occurred:', error);
    }
  };

  return (
    <Box>
      <Text fontSize="xl" mb="4">Listeners</Text>
      {listeners.map(listener => (
  <Flex justifyContent="center" alignItems="center" height="100%">
    <Box bg="white" shadow="md" p="6" rounded="md" mb="4" w="2xl">
      <Flex justify="space-between">
        <Stack spacing={3}>
          <Text fontWeight="bold">Listener Type: {listener.type}</Text>
          <Text>ID: {listener.ID}</Text>
          {listener.type === 'Redirector/HTTPS' ? (
            <>
              <Text>Interface: {listener.interface}</Text>
              <Text>Domain: {listener.domain}</Text>
            </>
          ) : (
            <Text>Interface: {listener.interface}</Text>
          )}
          {listener.type === 'TCP' && (
            <Text>Note: Can only interact with TCP implant through command line, access through callbacks in the web UI will cause errors.</Text>
          )}
        </Stack>
        <Stack spacing={3}>
          <Text><i className="fa fa-cog"></i> Port: {listener.port}</Text>
          <Text><i className="fa fa-eye"></i> Status: {listener.status}</Text>
          <Button colorScheme="red" mt="2" onClick={killModal.onOpen}>Kill</Button>
          <Button colorScheme="blue" mt="2" onClick={() => handleCompile(listener)}>
            {compilingListenerId === listener.ID ? <Spinner /> : 'Compile Implant'}
          </Button>
        </Stack>
      </Flex>
    </Box>
  </Flex>
))}
      <Modal isOpen={killModal.isOpen} onClose={killModal.onClose}>
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Feature Coming Soon</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            This feature is under development and will be available in a future version of the application.
          </ModalBody>
        </ModalContent>
      </Modal>
    </Box>
  );
}

function Listener() {
  const toast = useToast();
  const { register, handleSubmit } = useForm();
  const [listenerType, setListenerType] = useState('');
  const [isOpen, setIsOpen] = useState(false);
  const { data: listenerTypes, isLoading } = useQuery('listenerTypes', fetchListenerTypes);
  const { data: networkInterfaces, isLoading: interfacesLoading } = useQuery('interfaces', fetchInterfaces);

  const fetchListeners = async () => {
    const response = await fetch('/api/listeners');
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    return response.json();
  };

  const mutation = useMutation(startListener, {
    onSuccess: (data) => {
      toast({
        title: "Listener started",
        description: data.message,
        status: "success",
        duration: 9000,
        isClosable: true,
      });
      setIsOpen(false);
      fetchListeners();
    },
    onError: (error) => {
      toast({
        title: "An error occurred.",
        description: error.message,
        status: "error",
        duration: 9000,
        isClosable: true,
      });
    },
  });

  const handleStartListener = (data) => {
    let listenerData;
    if (listenerType === 'HTTP' || listenerType === 'TCP') {
      listenerData = {
        interface: data.interface,
        port: data.port,
        listenerType: listenerType,
      };
    } else if (listenerType === 'Redirector/HTTPS') {
      listenerData = {
        domain: data.domain,
        listenerType: listenerType,
      };
    }
    mutation.mutate(listenerData);
  };

  const handleSelectChange = (e) => {
    setListenerType(e.target.value);
    setIsOpen(true);
  };

  return (
    <Box my={3}>
      <Box p={5} shadow="md" borderWidth="1px" borderRadius="md" mb={5}>
        <Heading size="lg" mb={5}>PrimusC2 Listener Generation</Heading>
        <Text>Please select a listener type below:</Text>
        <Select placeholder="Select listener type" onChange={handleSelectChange} marginTop="4" >
          {isLoading ? (
            <Box padding={4}>
              <Spinner />
            </Box>
          ) : (
            listenerTypes.map((type) => (
              <option key={type} value={type}>
                {type}
              </option>
            ))
          )}
        </Select>
        <Modal isOpen={isOpen} onClose={() => setIsOpen(false)}>
          <ModalOverlay />
          <ModalContent>
            <ModalHeader>Configure Listener</ModalHeader>
            <ModalCloseButton />
            <ModalBody>
            <form onSubmit={handleSubmit(handleStartListener)}>
              {listenerType === 'HTTP' && (
                <>
                  <FormControl>
                    <FormLabel>Select interface:</FormLabel>
                    <Select {...register('interface')}>
                      {interfacesLoading ? (
                        <Box padding={4}>
                          <Spinner />
                        </Box>
                      ) : (
                        networkInterfaces.map((networkInterface) => (
                          <option key={networkInterface} value={networkInterface}>
                            {networkInterface}
                          </option>
                        ))
                      )}
                    </Select>
                  </FormControl>
                  <FormControl>
                    <FormLabel>Port:</FormLabel>
                    <Input type="number" {...register('port')} />
                  </FormControl>
                </>
              )}
              {listenerType === 'Redirector/HTTPS' && (
                <FormControl>
                  <FormLabel>Enter domain to call back to:</FormLabel>
                  <Input type="text" {...register('domain')} placeholder="foo.example.com" />
                </FormControl>
              )}
              {listenerType === 'TCP' && (
                <>
                  <FormControl>
                    <FormLabel>Select interface:</FormLabel>
                    <Select {...register('interface')}>
                      {interfacesLoading ? (
                        <Box padding={4}>
                          <Spinner />
                        </Box>
                      ) : (
                        networkInterfaces.map((networkInterface) => (
                          <option key={networkInterface} value={networkInterface}>
                            {networkInterface}
                          </option>
                        ))
                      )}
                    </Select>
                  </FormControl>
                  <FormControl>
                    <FormLabel>Port:</FormLabel>
                    <Input type="number" {...register('port')} />
                  </FormControl>
                </>
              )}
              <Button type="submit" isLoading={mutation.isLoading} marginTop="4">
                Start Listener
              </Button>
            </form>
            </ModalBody>
          </ModalContent>
        </Modal>
      </Box>
      <Box p={5} shadow="md" borderWidth="1px" borderRadius="md">
        <Heading size="lg" mb={5}>Listeners</Heading>
        <ListenerList fetchListeners={fetchListeners} />
      </Box>
    </Box>
  );
}

export default Listener;