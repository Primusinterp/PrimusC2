import React, { useEffect, useState } from 'react';
import { Box, Heading, Text, Flex, Stat, StatLabel, StatNumber, Image, Button } from '@chakra-ui/react';
import { Link } from 'react-router-dom';

function Home() {
  const [callbacksCount, setCallbacksCount] = useState(0);
  const [listenersCount, setListenersCount] = useState(0);
  const [payloadsCount, setPayloadsCount] = useState(0); 

  useEffect(() => {
    
    fetch('/api/callbacks')
      .then(response => response.json())
      .then(data => setCallbacksCount(data.length));

    fetch('/api/listeners')
      .then(response => response.json())
      .then(data => setListenersCount(data.length));

    fetch('/api/payloads') 
      .then(response => response.json())
      .then(data => setPayloadsCount(data.length));
  }, []);

  return (
    <Flex direction="column" justifyContent="center" alignItems="center" height="100vh">
      <Box backgroundColor="#2e353d" py={3} px={5} borderRadius="md">
        <Flex justifyContent="center">
          <Image src="/PrimusC2_transp.png" alt="PrimusC2 Logo" />
        </Flex>
      </Box>
      <Box my={3}>
        <Heading>Welcome to the <Text as="span" color="red">PrimusC2</Text> Interface</Heading>
        <Text>This is the home page. You can navigate to other pages using the menu on the left.</Text>
        <Flex marginTop={3} justifyContent="space-between" width="100%">
          <Link to="/listener"><Button backgroundColor="#2e353d" color="white" borderRadius="md" minWidth="200px">Listener Generation</Button></Link>
          <Link to="/callbacks"><Button backgroundColor="#2e353d" color="white" borderRadius="md" minWidth="200px">Callback interaction</Button></Link>
          <Link to="/payloads"><Button backgroundColor="#2e353d" color="white" borderRadius="md" minWidth="200px">Payloads</Button></Link>
        </Flex>
      </Box>
      <Flex marginTop={5}>
        <Box p={5} shadow="md" borderWidth="1px" borderRadius="md" marginRight={3}>
          <Stat>
            <StatLabel>Callbacks</StatLabel>
            <StatNumber>{callbacksCount}</StatNumber>
          </Stat>
        </Box>
        <Box p={5} shadow="md" borderWidth="1px" borderRadius="md" marginRight={3}>
          <Stat>
            <StatLabel>Listeners</StatLabel>
            <StatNumber>{listenersCount}</StatNumber>
          </Stat>
        </Box>
        <Box p={5} shadow="md" borderWidth="1px" borderRadius="md"> 
          <Stat>
            <StatLabel>Payloads</StatLabel>
            <StatNumber>{payloadsCount}</StatNumber>
          </Stat>
        </Box>
      </Flex>
    </Flex>
  );
}

export default Home;