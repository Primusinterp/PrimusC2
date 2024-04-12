import React from 'react';
import { ChakraProvider, Box, Flex, Link, Image } from '@chakra-ui/react';
import { FaHome, FaListAlt, FaRetweet, FaBug, FaRocket } from 'react-icons/fa';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import Home from './Home';
import Listener from './Listener';
import Callbacks from './Callbacks';
import Interact from './Interact';
import Payloads from './Payloads'; 

const queryClient = new QueryClient();

function App() {
  return (
    <ChakraProvider>
      <QueryClientProvider client={queryClient}>
        <Router>
          <Flex>
            <Box bg="#2e353d" color="white" width="350px" height="100vh" position="fixed">
              <Box bg="#23282e" display="flex" justifyContent="center" alignItems="center" padding={5}>
                <Image src="/PrimusC2_transp.png" alt="Logo" boxSize="250px" />
              </Box>
              <Flex direction="column" align="start">
                <Box as={Link} href="/" display="flex" alignItems="center" padding={2} borderBottom="1px solid #666" width="100%" _hover={{ bg: "white", color: "#2e353d" }}>
                  <FaHome boxSize={6} />
                  <Box marginLeft={2}>Home</Box>
                </Box>
                <Box as={Link} href="/listener" display="flex" alignItems="center"  padding={2} borderBottom="1px solid #666" width="100%" _hover={{ bg: "white", color: "#2e353d" }}>
                  <FaListAlt boxSize={6} />
                  <Box marginLeft={2}>Listener</Box>
                </Box>
                <Box as={Link} href="/callbacks" display="flex" alignItems="center"  padding={2} borderBottom="1px solid #666" width="100%" _hover={{ bg: "white", color: "#2e353d" }}>
                  <FaRetweet boxSize={6} />
                  <Box marginLeft={2}>Callbacks</Box>
                </Box>
                <Box as={Link} href="/payloads" display="flex" alignItems="center" padding={2} borderBottom="1px solid #666" width="100%" _hover={{ bg: "white", color: "#2e353d" }}>
                  <FaRocket boxSize={6} />
                  <Box marginLeft={2}>Payloads</Box>
                </Box>
              </Flex>
            </Box>
            <Box flex="1" marginLeft="350px">
              <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/listener" element={<Listener />} />
                <Route path="/callbacks" element={<Callbacks />} />
                <Route path="/interact/:id" element={<Interact />} /> 
                <Route path="/payloads" element={<Payloads />} /> 
              </Routes>
            </Box>
          </Flex>
        </Router>
      </QueryClientProvider>
    </ChakraProvider>
  );
}

export default App;