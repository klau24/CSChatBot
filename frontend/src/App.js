import logo from './logo.svg';
import './App.css';
import { Button } from 'bootstrap';
import axios from "axios";

function sendGet(){
  axios.get("http://localhost:5000/" + "Where are Lups office Hours").then((response) => console.log(response.data))
  
}

function App() {

  return (
    <div className="App">
      <header className="App-header">
        <img src={logo} className="App-logo" alt="logo" />
        <button onClick={sendGet}> Hello

        </button>
        <a
          className="App-link"
          href="https://reactjs.org"
          target="_blank"
          rel="noopener noreferrer"
        >
          Learn React
        </a>
      </header>
    </div>
  );
}

export default App;
