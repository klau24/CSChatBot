import React, { Component } from "react";




function Message(message,index){
    if(index%2==0){
        return (
            <p key={index} className="message" style={{background:'white',margin:"0px",padding:"10px"}}>{message.text}</p>
        )
    }
    return (
        <p key={index} className="message" style={{background:'#d9dadb',height:"100%",margin:"0px",padding:"10px"}}>{message.text} </p>
    )
}

export default class ChatWindow extends Component {
  componentDidUpdate = (prevProps, prevState) => {
    if (this.props.messagesList !== prevProps.messagesList) {
      this.messageListEnd.scrollIntoView({ behavior: "smooth" });
    }
  };

  render() {
    const { messagesList } = this.props;
    return (
      <div className="chat-window">
        <div className="box">
          <div className="inner">
            {Array.isArray(messagesList) &&
              messagesList.map((oneMessage, index) => (
                Message(oneMessage,index)

              ))}
            <div
              className="reference"
              ref={node => (this.messageListEnd = node)}
            />
          </div>
        </div>
      </div>
    );
  }
}
