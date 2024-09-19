import React, { useState, useEffect, useRef } from 'react';
import { Box, Button, VStack, Text, Flex, List, ListItem, Icon } from '@chakra-ui/react';
import { CheckCircleIcon, WarningIcon, InfoOutlineIcon, TimeIcon } from '@chakra-ui/icons';
import { useParams } from 'react-router-dom';
import Autosuggest from 'react-autosuggest';

function Interact() {
  const { id } = useParams();
  const [input, setInput] = useState('');
  const targetId = id.split(' ')[0];
  const lastMessageRef = useRef(null);
  const [callbackData, setCallbackData] = useState([]);
  const [messages, setMessages] = useState([]);
  const [commands, setCommands] = useState([]);
  const [suggestions, setSuggestions] = useState([]);
  const [commandHistory, setCommandHistory] = useState([]);

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

  const fetchCallbackData = () => {
    fetch(`/api/callbackdata_by_id/${targetId}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    })
      .then(response => response.json())
      .then(data => {
        setCallbackData(data);
        console.log('Callback Data:', data);
      })
      .catch((error) => {
        console.error('Error fetching callback data:', error);
      });
  };

  useEffect(() => {
    fetchCallbackData();
  }, [targetId]);

  useEffect(() => {
    const fetchCommandHistory = () => {
      fetch(`/api/fetch_command_history?target_id=${encodeURIComponent(targetId)}`)
        .then(response => response.json())
        .then(data => {
          const formattedData = data.flatMap(item => {
            const [command, ...result] = item.split('\n');
            const operatorMessageAndCommand = /\[OPERATOR\] - (Mon|Tue|Wed|Thu|Fri|Sat|Sun), \d{1,2} (Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) \d{4} \d{2}:\d{2}:\d{2} UTC: .+/;
            const highlight = operatorMessageAndCommand.test(command);
            return [{ text: command, sender: 'server', highlight }, { text: result.join('\n'), sender: 'server', highlight: false }];
          });
          setMessages(prev => [...prev, ...formattedData]);
        })
        .catch(error => console.error('Error fetching command history:', error));
    };
  
    fetchCommandHistory();
  }, [targetId]);

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

  useEffect(() => {
    localStorage.setItem(`messages-${id}`, JSON.stringify(messages));
  }, [messages, id]);

  useEffect(() => {
    const fetchResults = () => {
      fetch(`/api/get_results?target_id=${targetId}`)
      .then(response => response.json())
      .then(data => {
        if (data.results.status === 'success') {
          data.results.results.forEach(result => {
            setMessages(prev => [...prev, { text: result, sender: 'server' }]);
          });
          // Fetch callback data after receiving results
          fetchCallbackData();
        }
      })
      .catch((error) => {
        console.error('Error:', error);
      });
    };
    
    const interval = setInterval(fetchResults, 5000);
    
    return () => clearInterval(interval);
  }, [targetId]);

  useEffect(() => {
    lastMessageRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = () => {
    const date = new Date();
    const dateString = date.toUTCString().split(' ').slice(0, 5).join(' ');
    const formattedInput = `[OPERATOR] - ${dateString}: ${input}`;
  
    setMessages(prev => [...prev, { text: formattedInput, sender: 'user', highlight: true }]);
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
      if (data.message && data.message !== input) {
        setMessages(prev => [...prev, { text: data.message, sender: 'server', highlight: false }]);
      }
      // Fetch callback data after sending a command
      fetchCallbackData();
    })
    .catch((error) => {
      console.error('Error:', error);
    });
    setInput('');
  };

  const renderIcon = (key, value) => {

    const lowerKey = key.toLowerCase();
    const lowerValue = value !== null && value !== undefined ? value.toString().toLowerCase() : '';

    if (lowerValue.includes('active') || lowerValue.includes("disabled") || lowerValue.includes("yes")) {
      return <CheckCircleIcon color="green.500" />;
    } else if (lowerValue.includes('no') || key.toLowerCase().includes('running')) {
      return <WarningIcon color="red.500" />;
    } else if (lowerKey.includes('time')) {
      return <TimeIcon color="blue.500" />;
    } else if (lowerValue.includes('Dead')) {
      return <WarningIcon color="red.500" />;
    } else {
      return <InfoOutlineIcon color="blue.500" />;
    }
  };

  return (
    <Flex direction="column" justifyContent="space-between" height="100vh" p={5} bg="black">
      <Box>
        <Text mb={5} color="green.300" fontFamily="monospace">Interacting with callback {id}</Text>
        <VStack align="stretch" spacing={3} overflowY="auto" maxHeight="80vh">
          {messages.map((message, index) => (
            <Box key={index} alignSelf="flex-start" ref={index === messages.length - 1 ? lastMessageRef : null}>
              <pre style={{
                color: message.highlight ? 'darkgoldenrod' : 'rgb(173, 216, 230)',
                fontFamily: 'monospace',
                wordWrap: 'break-word',
                overflowWrap: 'break-word',
                whiteSpace: 'pre-wrap',
              }}>
                {message.text}
              </pre>
            </Box>
          ))}
        </VStack>
      </Box>

      <Box position="fixed" left="0" bottom="0" bg="#23282e" color="white" p={4} borderRadius="30px" width="350px" maxHeight="50%" overflowY="auto" boxShadow="lg" >
        <Text fontSize="lg" fontWeight="bold" mb={2}>Callback Data:</Text>
        {callbackData && callbackData.length > 0 ? (
          callbackData.map((dataItem, index) => (
            <Box key={index} mb={4} borderBottom="1px solid white" pb={2}>
              <List spacing={2}>
                {Object.entries(dataItem).map(([key, value]) => (
                  <ListItem key={key} display="flex" alignItems="center">
                    {renderIcon(key, value)}
                    <Text ml={2} fontWeight="bold">{key}:</Text>
                    <Text ml={1}>{value !== null ? value.toString() : 'N/A'}</Text>
                  </ListItem>
                ))}
              </List>
            </Box>
          ))
        ) : (
          <Text>No data available</Text>
        )}
      </Box>

      <Box>
        <Autosuggest
          suggestions={suggestions}
          onSuggestionsFetchRequested={({ value }) => {
            const inputValue = value.trim().toLowerCase().split(" ").pop();
            const inputLength = inputValue.length;
            const newSuggestions = inputLength === 0 ? [] : commands.filter(cmd =>
              cmd.toLowerCase().slice(0, inputLength) === inputValue
            );
            setSuggestions(newSuggestions);
          }}
          onSuggestionsClearRequested={() => setSuggestions([])}
          getSuggestionValue={suggestion => suggestion}
          renderSuggestion={suggestion => <div>{suggestion}</div>}
          inputProps={{
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
          }}
          theme={theme}
        />
        <Button onClick={handleSend} colorScheme="green">Send</Button>
      </Box>
    </Flex>
  );
}

export default Interact;