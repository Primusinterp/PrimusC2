import React, { useEffect, useState } from 'react';
import { Box, Text, Button, Flex, Grid, Heading, Link } from '@chakra-ui/react';
import { ChatIcon, TimeIcon } from '@chakra-ui/icons';
import { Link as RouterLink } from 'react-router-dom';

function Callbacks() {
  const [callbacks, setCallbacks] = useState([]);

  useEffect(() => {
    const fetchCallbacks = () => {
      fetch('/api/callbacks') 
        .then(response => response.json())
        .then(newCallbacks => {
          setCallbacks(prevCallbacks => {
            
            const prevCallbacksMap = new Map(prevCallbacks.map(callback => [callback.id, callback]));
  
            
            const uniqueNewCallbacks = newCallbacks.filter(callback => !prevCallbacksMap.has(callback.id));
  
            
            return prevCallbacks.concat(uniqueNewCallbacks);
          });
        })
        .catch((error) => {
          console.error('Error:', error);
        });
    };
  
    fetchCallbacks(); 
    const intervalId = setInterval(fetchCallbacks, 5000); 
  
    return () => {
      clearInterval(intervalId); 
    };
  }, []);

  if (callbacks.length === 0) {
    return (
      <Flex justifyContent="center" alignItems="center" height="100vh">
        <Text>No callbacks received yet :(</Text>
      </Flex>
    );
  }

  return (
    <Flex direction="column" alignItems="center">
      <Heading mb={10}>Callbacks</Heading>
      {callbacks.map(callback => (
        <Box bg="white" shadow="md" p="6" rounded="md" mb="6" width="50vw">
          <Grid templateColumns="repeat(2, 1fr)" gap={6}>
            <Box>
              <Text fontWeight="bold">Callback ID: {callback.id}</Text>
              <Text>Last Callback: {callback.time}</Text>
            </Box>
            <Box>
              <Flex><Text fontWeight="bold" mr={2}><TimeIcon /> Admin:</Text><Text>{callback.admin}</Text></Flex>
              <Flex><Text fontWeight="bold" mr={2}><ChatIcon /> Target:</Text><Text>{callback.target}</Text></Flex>
              <Flex><Text fontWeight="bold" mr={2}><ChatIcon /> Username:</Text><Text>{callback.username}</Text></Flex>
              <Flex><Text fontWeight="bold" mr={2}><ChatIcon /> Status:</Text><Text>{callback.status}</Text></Flex>
              <Flex><Text fontWeight="bold" mr={2}><ChatIcon /> OS:</Text><Text>{callback.os}</Text></Flex>
              <Flex><Text fontWeight="bold" mr={2}><ChatIcon /> AMSI:</Text><Text>{callback.amsi}</Text></Flex>
            </Box>
          </Grid>
          <Link as={RouterLink} to={`/interact/${callback.id}`}><Button colorScheme="blue" mt="2">Interact</Button></Link>
          </Box>
      ))}
    </Flex>
  );
}

export default Callbacks;