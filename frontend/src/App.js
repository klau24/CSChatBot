
import './App.css';
import React, { Component } from "react";
import ReactDOM from "react-dom";
import axios from "axios";
import ChatWindow from "./ChatWindow";
import "bootstrap/dist/css/bootstrap.min.css";
// Bootstrap Bundle JS
import "bootstrap/dist/js/bootstrap.bundle.min";



export default class App extends Component {
  constructor(props) {
    super(props);
    this.state = { messages: [ ] };
  }

  sendGet = async (message) => {
    const response = await axios.get("http://localhost:5000/" + message.text);
    if (response.status === 200) { // response - object, eg { status: 200, message: 'OK' }
      console.log("Hello")
      
      console.log(Array(response.data.slice(-1)[0]))
      const newMessage = { text: response.data.slice(-2)[0] };
      
      let updatedMessages = [...this.state.messages,newMessage];
      this.setState({
        messages: updatedMessages
      });
      return response.data[0];
    }

  }

  submitted = getNewMessage => {
    if (getNewMessage != "") {
      const newMessage = { text: getNewMessage };
      let updatedMessages = [...this.state.messages, newMessage];
      this.sendGet(newMessage)
      this.setState({
        messages: updatedMessages
      });
    }
  };

  state = {
    new: ""
  };

  handleSubmit = event => {
    event.preventDefault();
    this.submitted(this.state.new);
    this.setState({
      new: ""
    });
  };

  handleCompose = event => {
    let typedValue = event.target.value;
    if (typedValue != "" && typedValue != " ") {
      this.setState({
        new: event.target.value
      });
    }
  };

  render() {
    return (
      <div className="App" style={{height:"100vh"}}>
        <h1 style={{background:"#154734",color:"white",height:"10%", margin:"0px",lineHeight:'200%', paddingTop:""}}>Cal Poly Virtual Assistant</h1>
        <div className='row' style={{background:"", height:"90%", margin:"0px"}}>
          <div className='col-2' style={{background:"#BD8813"}}></div>
          <div className='col-10' style={{background:""}}> 
            <div style={{border:"0px solid red", marginTop:"20px", height:"85%"}}>
              <ChatWindow messagesList={this.state.messages} />
            </div>

            <form onSubmit={this.handleSubmit}>
              <input
                style={{margin:"30px auto auto auto",width:"65%", height:"45px",position:"relative",borderRadius: "0.375rem"}}
                className="form-control"
                placeholder="Ask a Question"
                onChange={this.handleCompose}
                value={this.state.new}
              />
            </form>

         </div>
        </div>
      </div>
    );
  }
}
