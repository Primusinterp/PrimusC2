import React, { useEffect, useState, useMemo } from 'react';
import { useParams } from 'react-router-dom';
import Autosuggest from 'react-autosuggest';
import { Link } from 'react-router-dom';

function CommandHistorySearch() {
  const { id } = useParams();
  const [callbacks, setCallbacks] = useState([]);
  const [commandHistories, setCommandHistories] = useState({});
  const [searchQuery, setSearchQuery] = useState('');
  const [suggestions, setSuggestions] = useState([]);
  const [displayResults, setDisplayResults] = useState(false);

  const getSuggestions = value => {
    const inputValue = value.trim().toLowerCase();
    const inputLength = inputValue.length;
  
    return inputLength === 0 ? [] : Object.keys(commandHistories).filter(cmd =>
      typeof cmd === 'string' && cmd.toLowerCase().slice(0, inputLength) === inputValue
    );
  };

  const onSuggestionsFetchRequested = ({ value }) => {
    setSuggestions(getSuggestions(value));
  };

  const onSuggestionsClearRequested = () => {
    setSuggestions([]);
  };

  const inputProps = {
    value: searchQuery,
    onChange: (event, { newValue }) => {
      setSearchQuery(newValue);
      setDisplayResults(true);
    },
    placeholder: "Search callback output..."
  };

  useEffect(() => {
    const fetchCallbacks = () => {
      fetch(`/api/callbacks`) 
        .then(response => response.json())
        .then(newCallbacks => {
          setCallbacks(newCallbacks);
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
  }, [id]); 

  useEffect(() => {
    callbacks.forEach(callbackId => {
      fetch(`/api/fetch_command_history?target_id=${callbackId.id}`)
        .then(response => response.json())
        .then(data => {
          const commandHistoryString = data.join('\n');
          setCommandHistories(prev => ({ ...prev, [callbackId.id]: commandHistoryString }));
        })
        .catch((error) => {
          console.error('Error:', error);
        });
    });
  }, [callbacks]);

  const filteredCommandHistories = useMemo(() => 
    Object.entries(commandHistories)
      .filter(([callbackId, commandHistory]) => 
        typeof commandHistory === 'string' && commandHistory.toLowerCase().includes(searchQuery.toLowerCase())
      )
  , [commandHistories, searchQuery]);

  return (
    <div style={{ fontFamily: 'Arial, sans-serif' }}>
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '10vh' }}>
        <Autosuggest
          suggestions={suggestions}
          onSuggestionsFetchRequested={onSuggestionsFetchRequested}
          onSuggestionsClearRequested={onSuggestionsClearRequested}
          getSuggestionValue={suggestion => suggestion}
          renderSuggestion={suggestion => <div>{suggestion}</div>}
          inputProps={inputProps}
          theme={{
            input: {
              width: 400,
              height: 30,
              padding: '10px 20px',
              fontSize: 16,
              border: '1px solid #aaa',
              borderRadius: 20,
              backgroundImage: 'url(https://icon-library.com/images/magnifying-glass-icon-png/magnifying-glass-icon-png-2.jpg)',
              backgroundPosition: '98% center',
              backgroundRepeat: 'no-repeat',
              backgroundSize: '20px',
            },
            suggestionsList: {
              margin: 0,
              padding: 0,
              listStyleType: 'none',
            },
            suggestion: {
              cursor: 'pointer',
              padding: '10px 20px',
            },
            suggestionHighlighted: {
              backgroundColor: '#ddd',
            },
          }}
        />
      </div>
      {displayResults && filteredCommandHistories.length > 0 ? (
        filteredCommandHistories.map(([callbackId, commandHistory]) => (
          <div key={callbackId} style={{ margin: '20px', padding: '20px', border: '1px solid #ddd', borderRadius: '5px', backgroundColor: '#f6f8fa' }}>
            <h2 style={{ color: '#333' }}>Callback ID: <Link to={`/interact/${callbackId}`} style={{ color: '#1634c9' }}>{callbackId}</Link></h2>
            <pre style={{ whiteSpace: 'pre-wrap', wordWrap: 'break-word', backgroundColor: '#f6f8fa', padding: '10px', borderRadius: '5px' }}>
              {commandHistory.split('\n').map((line, index) => (
                <React.Fragment key={index}>
                  <span style={{ color: line.trim().startsWith('[OPERATOR]') ? 'orange' : 'black' }}>
                    {line}
                  </span>
                  {'\n'}
                </React.Fragment>
              ))}
            </pre>
          </div>
        ))
      ) : (
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '90vh' }}>
          <p>No results matched you search</p>
        </div>
      )}
    </div>
  );
}

export default CommandHistorySearch;
