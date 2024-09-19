import React, { useEffect, useState } from 'react';
import { Box, Text, Button, Flex, Grid, Heading, Link, Input, IconButton } from '@chakra-ui/react';
import { ChatIcon, TimeIcon, CheckIcon } from '@chakra-ui/icons';
import { Textarea } from '@chakra-ui/react';
import { Link as RouterLink } from 'react-router-dom';

function Callbacks() {
  const [callbacks, setCallbacks] = useState([]);
  const [notes, setNotes] = useState({});
  const [editing, setEditing] = useState(null); // Track editing state

  const saveNote = (id, note) => {
    fetch(`/api/update_note`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ id, note }),
    })
    .then(response => response.json())
    .then(data => {
      console.log('Success:', data);
      // Update the specific callback's note after successful save
      setCallbacks(callbacks.map(callback => 
        callback.id === id ? {...callback, notes: note} : callback
      ));
      setNotes(prevNotes => ({ ...prevNotes, [id]: note }));
      setEditing(null); // Exit editing mode after saving
    })
    .catch((error) => {
      console.error('Error:', error);
    });
  };

  useEffect(() => {
    const fetchCallbacks = () => {
      fetch('/api/callbacks') 
        .then(response => response.json())
        .then(newCallbacks => {
          setCallbacks(prevCallbacks => {
            const prevCallbacksMap = new Map(prevCallbacks.map(callback => [callback.id, callback]));
            return newCallbacks.map(newCallback => {
              const prevCallback = prevCallbacksMap.get(newCallback.id);
              return prevCallback && editing === newCallback.id
                ? prevCallback // Keep the current callback if editing
                : newCallback;
            });
          });
        })
        .catch((error) => {
          console.error('Error:', error);
        });
    };

    if (editing === null) {
      fetchCallbacks(); 
      const intervalId = setInterval(fetchCallbacks, 5000); 
  
      return () => {
        clearInterval(intervalId);
      };
    }
  }, [editing]);  // Add editing to the dependency array

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
        <Box key={callback.id} bg="white" shadow="md" p="6" rounded="md" mb="6" width="50vw">
          <Grid templateColumns="repeat(2, 1fr)" gap={6}>
            <Box>
              <Text fontWeight="bold">Callback ID: {callback.id}</Text>
              <Text>Last Callback: {callback.latest_callbacktime}</Text>
              <Flex mt={2}>
                <Textarea 
                  size="sm" 
                  width="50%" 
                  height="100px" 
                  value={notes[callback.id] !== undefined ? notes[callback.id] : callback.notes || ''} 
                  onChange={e => setNotes(prevNotes => ({ ...prevNotes, [callback.id]: e.target.value }))} 
                  placeholder="Enter a note" 
                  onFocus={() => setEditing(callback.id)}
                />
                {/* Show Save button if the note was modified, even if it's empty */}
                {notes[callback.id] !== undefined && notes[callback.id] !== callback.notes && (
                <IconButton 
                  aria-label="Save note" 
                  icon={<CheckIcon />} 
                  onClick={() => saveNote(callback.id, notes[callback.id])} 
                />
              )}
              </Flex>

            </Box>
            <Box>
              <Flex>
                <Text fontWeight="bold" mr={2}><ChatIcon /> Admin:</Text>
                <Text>{callback.adminStatus}</Text>
              </Flex>
              <Flex>
                <Text fontWeight="bold" mr={2}><ChatIcon /> Target:</Text>
                <Text>{callback.target}</Text>
              </Flex>
              <Flex>
                <Text fontWeight="bold" mr={2}><ChatIcon /> Username:</Text>
                <Text>{callback.username}</Text>
              </Flex>
              <Flex>
                <Text fontWeight="bold" mr={2}><ChatIcon /> Status:</Text>
                <Text>{callback.status}</Text>
              </Flex>
              <Flex>
                <Text fontWeight="bold" mr={2}><ChatIcon /> OS:</Text>
                <Text>{callback.OS}</Text>
              </Flex>
              <Flex>
                <Text fontWeight="bold" mr={2}><ChatIcon /> AMSI:</Text>
                <Text>{callback.amsi}</Text>
              </Flex>
              <Flex>
                <Text fontWeight="bold" mr={2}><ChatIcon /> Sleep Interval:</Text>
                <Text>{callback.sleep_interval}</Text>
              </Flex>
            </Box>
          </Grid>
          <Link as={RouterLink} to={`/interact/${callback.id}`}>
            <Button colorScheme="blue" mt="2">Interact</Button>
          </Link>
        </Box>
      ))}
    </Flex>
  );
}

export default Callbacks;
