import React, { useState, useEffect } from 'react';
import { Box, Heading, Text,Input, Button,  Table,Thead,Tr,Th,Tbody,Td,FormLabel, FormControl, useDisclosure, Modal, ModalOverlay, ModalContent, ModalHeader, ModalCloseButton, ModalBody, ModalFooter, useToast } from '@chakra-ui/react';

function Payloads() {
    const [payloads, setPayloads] = useState([]); 
    const [file, setFile] = useState(null); 
    const { isOpen, onOpen, onClose } = useDisclosure(); 
    const toast = useToast();

    useEffect(() => {
        fetch('/api/payloads') 
        .then(response => response.json())
        .then(data => setPayloads(data))
        .catch(error => console.error('Error:', error));
    }, [file]);

  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
  };

  const handleUpload = () => {
    const formData = new FormData();
    formData.append('file', file);

    fetch('/api/upload', { 
      method: 'POST',
      body: formData
    })
    .then(response => response.text())
    .then(result => {
      console.log('Success:', result);
      toast({
        title: "File uploaded",
        description: result,
        status: "success",
        duration: 9000,
        isClosable: true,
      });
      setPayloads(prevPayloads => [...prevPayloads, file.name]);
    })
    .catch(error => {
      console.error('Error:', error);
      toast({
        title: "An error occurred.",
        description: error.message,
        status: "error",
        duration: 9000,
        isClosable: true,
      });
    });
  };

  return (
    <Box p={5}>
      <Heading as="h2" mb={5}>Payloads</Heading>
      <FormControl>
        <FormLabel>Upload a file</FormLabel>
        <Input type="file" onChange={handleFileChange} p={1} height="auto" />
      </FormControl>
      <Button colorScheme="blue" mt={3} onClick={handleUpload}>Upload</Button>
      <Heading as="h4" mt={5} mb={2}>Available Payloads:</Heading>
      <Text mb={2}>
        This is all the payloads available in the /Payloads folder, these can either be used to transfer to a target or they can be .NET assemblies that can be executed in memory using execute-ASM.
      </Text>

      
      <Table variant="simple">
        <Thead>
          <Tr>
            <Th>Payloads</Th>
          </Tr>
        </Thead>
        <Tbody>
          {payloads.map((payload, index) => (
            <Tr key={index}>
              <Td>{payload}</Td>
            </Tr>
          ))}
        </Tbody>
      </Table>



      
      <Modal isOpen={isOpen} onClose={onClose}>
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Upload Status</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <Text>File uploaded successfully</Text>
          </ModalBody>
          <ModalFooter>
            <Button colorScheme="blue" mr={3} onClick={onClose}>
              Close
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </Box>
  );
}

export default Payloads;