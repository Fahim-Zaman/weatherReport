import React, { useState } from 'react';
import axios from 'axios';
import './style.css';



console.log(process.env.REACT_APP_TO)
const TODAY_ID=process.env.REACT_APP_TO;
const UPCOMMING_ID=process.env.REACT_APP_UP;
const EMAIL_SUBS_ID=process.env.REACT_APP_EM;

const TODAY = 'https://'+TODAY_ID+'.execute-api.us-east-1.amazonaws.com/oneday/today';
const UPCOMMING = 'https://'+UPCOMMING_ID+'.execute-api.us-east-1.amazonaws.com/upcomming/fivedays';
const EMAIL_SUBS='https://'+EMAIL_SUBS_ID+'.execute-api.us-east-1.amazonaws.com/email/subscription';



function App() {


  const [location, setLocation] = useState('');
  const [weatherData, setWeatherData] = useState(null);
  const [error, setError] = useState('');
  const [subscriber, setSubscriber] = useState({
    email: '',
    subscribeLocation: '',
  });

  const handleSearchToday = () => {
    setError('');
    setWeatherData(null);

    // Call the backend API to fetch today's weather data
    axios.get(TODAY+'?location='+location)
      .then(response => {
        setWeatherData(response.data);
       
      })
      .catch(error => {
        setError('Error fetching weather data. Please try again later.');
        console.error('Error fetching weather data:', error);
      });
  };

  const handleSearchUpcoming = () => {
    setError('');
    setWeatherData(null);

    // Call the backend API to fetch weather forecast for upcoming 5 days
    axios.get(UPCOMMING+'?location='+location)
      .then(response => {
        setWeatherData(response.data);
      })
      .catch(error => {
        setError('Error fetching weather data. Please try again later.');
        console.error('Error fetching weather data:', error);
      });
  };

  const handleSubscribe = () => {
    
    axios.get(EMAIL_SUBS+'?email='+subscriber.email+'&location='+subscriber.subscribeLocation)
    .then(response => {
      alert(response.data)
    })
    .catch(error => {
      setError('Error fetching weather data. Please try again later.');
      console.error('Error fetching weather data:', error);
    });

  };

  const handleInputChange = event => {
    const { name, value } = event.target;
    setSubscriber(prevState => ({ ...prevState, [name]: value }));
  };

  return (
    <div className="App">
      <div className="left-container">
        <h1>Weather App</h1>
        <p>To get notified with more details information <br></br>Plesae subscribe with your desire location </p>
        <input
          type="text"
          value={location}
          onChange={e => setLocation(e.target.value)}
          placeholder="Enter a location"
        />
        <div className="search-buttons">
          <button onClick={handleSearchToday}>Today's Weather</button>
          <button onClick={handleSearchUpcoming}>Upcoming 5 Days</button>
        </div>

        {error && <p className="error">{error}</p>}

        {weatherData && (
          <div className="weather-info">
            <h2>{weatherData[0].location}</h2>
            {weatherData.map((dayData, index) => (
              <div key={index}>
                <h3>{new Date(dayData.date).toDateString()}</h3>
                <p>Temperature: {dayData.temperature}°C</p>
                <p>Humidity: {dayData.humidity}%</p>
                <p>Weather: {dayData.weather}</p>
                <hr />
              </div>
            ))}
          </div>
        )}

        {!weatherData && !error && (
          <p>Enter a location and select an option to see the weather details.</p>
        )}
      </div>
      <div className="right-container">
        <h2>Subscribe for Weather Notifications</h2>
        <input
          type="text"
          name="email"
          value={subscriber.email}
          onChange={handleInputChange}
          placeholder="Enter your email"
        />
        <input
          type="text"
          name="subscribeLocation"
          value={subscriber.subscribeLocation}
          onChange={handleInputChange}
          placeholder="Enter a location to subscribe"
        />
        <button onClick={handleSubscribe}>Subscribe</button>
        <p>
          Subscribe for detailed information.<br />
          After your subscription, if you search for that location's weather, you will be notified via email.
        </p>
      </div>
    </div>
  );
}
export default App;
