import React, { useState, useEffect, useRef } from 'react';
import { Box, Button, VStack, Text, Flex } from '@chakra-ui/react';
import { useParams } from 'react-router-dom';
import Autosuggest from 'react-autosuggest';

function Interact() {
  const { id } = useParams();
  const [input, setInput] = useState('');
  const targetId = id.split(' ')[0];
  const lastMessageRef = useRef(null);
  const theme = {
    input: {
      fontFamily: 'monospace',
      color: 'green.300',
      backgroundColor: 'white',
      border: 'none',
      outline: 'none',
      width: '100%',
      maxWidth: '100vw',
      padding: '10px',
      boxSizing: 'border-box',
    },
    suggestionsContainer: {
        position: 'absolute',
        bottom: '88px', 
        backgroundColor: 'white',
        maxHeight: '500px',
        overflowY: 'auto',
        width: '100%',
    },
    suggestion: {
      padding: '10px',
      cursor: 'pointer',
    },
    suggestionHighlighted: {
      backgroundColor: '#ddd',
    },
  };

  const [messages, setMessages] = useState(() => {
    const savedMessages = localStorage.getItem(`messages-${id}`);
    if (savedMessages) {
      return JSON.parse(savedMessages);
    } else {
      return [];
    }
  });




  const [commands, setCommands] = useState([]);

  useEffect(() => {
    const fetchCommands = () => {
      fetch('/api/keywords') 
        .then(response => response.json())
        .then(data => setCommands(data)) 
        .catch((error) => {
          console.error('Error:', error);
        });
    };
  
    fetchCommands(); 
    const intervalId = setInterval(fetchCommands, 15000); 
  
    return () => {
      clearInterval(intervalId); 
    };
  }, []);

  const [suggestions, setSuggestions] = useState([]);

  const onSuggestionsFetchRequested = ({ value }) => {
    const newSuggestions = getSuggestions(value);
    setSuggestions(newSuggestions);
  };

  const onSuggestionsClearRequested = () => {
    setSuggestions([]);
  };

  const getSuggestions = value => {
    const inputValue = value.trim().toLowerCase().split(" ").pop();
    const inputLength = inputValue.length;
  
    return inputLength === 0 ? [] : commands.filter(cmd =>
      cmd.toLowerCase().slice(0, inputLength) === inputValue
    );
  };

  const inputProps = {
    className: 'react-autosuggest__input', 
    placeholder: "Type a command...",
    value: input,
    onChange: (event, { newValue, method }) => {
      if (method === 'enter' || method === 'click') {
        const words = input.split(" ");
        words.pop();
        words.push(newValue);
        setInput(words.join(" "));
      } else if (method !== 'down' && method !== 'up') {
        setInput(newValue);
      }
    },
    onKeyPress: e => {
      if (e.key === 'Enter') {
        handleSend();
      }
    },
  };

  useEffect(() => {
    localStorage.setItem(`messages-${id}`, JSON.stringify(messages));
  }, [messages, id]);

  const handleSend = () => {
    setMessages(prev => [...prev, { text: input, sender: 'user' }]);
    fetch('/api/interact', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        command: input,
        target_id: targetId,
      }),
    })
    .then(response => response.json())
    .then(data => {
      if (data.message) {
        setMessages(prev => [...prev, { text: data.message, sender: 'server' }]);
      }
    })
    .catch((error) => {
      console.error('Error:', error);
    });
    setInput('');
  };

  useEffect(() => {
    const targetId = id.split(' ')[2];
    const interval = setInterval(() => {
      fetch(`/api/get_results?target_id=${targetId}`)
      .then(response => response.json())
      .then(data => {
        if (data.result) {
            const result = atob(data.result);
            setMessages(prev => [...prev, { text: result, sender: 'server' }]);
          }
        })
        .catch((error) => {
          console.error('Error:', error);
        });
      }, 5000); 
    
      return () => clearInterval(interval); 
    }, [id]);

    useEffect(() => {
        lastMessageRef.current?.scrollIntoView({ behavior: 'smooth' });
      }, [messages]);
    
      return (
        <Flex direction="column" justifyContent="space-between" height="100vh" p={5} bg="black">
          <Box>
            <Text mb={5} color="green.300" fontFamily="monospace">Interacting with callback {id}</Text>
            <VStack align="stretch" spacing={3} overflowY="auto" maxHeight="80vh">
            {messages.map((message, index) => (
                <Box key={index} alignSelf="flex-start" ref={index === messages.length - 1 ? lastMessageRef : null}>
                    <pre style={{ 
                        color: message.sender === 'user' ? 'darkgoldenrod' : 'rgb(173, 216, 230)', 
                        fontFamily: 'monospace',
                        wordWrap: 'break-word', 
                        overflowWrap: 'break-word',
                        whiteSpace: 'pre-wrap', 
                    }}>
                        {message.sender === 'user' ? `[OPERATOR] - ${new Date().toUTCString().replace('GMT', 'UTC')}: ${message.text}` : message.text}
                    </pre>
                </Box>
                ))}
            </VStack>
          </Box>
          <Box>
            <Autosuggest
              suggestions={suggestions}
              onSuggestionsFetchRequested={onSuggestionsFetchRequested}
              onSuggestionsClearRequested={onSuggestionsClearRequested}
              getSuggestionValue={suggestion => suggestion}
              renderSuggestion={suggestion => <div>{suggestion}</div>}
              inputProps={inputProps}
              theme={theme}
            />
            <Button onClick={handleSend} colorScheme="green">Send</Button>
          </Box>
        </Flex>
      );
    }
    
    export default Interact;