import React, { Component } from "react";




function Message(message,index){
    if(index%2==0){
        return (
          <div style={{textAlign:"left", margin:"10px", marginLeft:"auto", marginRight:"15%", background:'#5fc9f8', position: "relative",width:"auto", maxWidth:"300px", height: "auto" , borderRadius: "30px", padding:"10px"}}>
            <p key={index} className="message" style={{margin:"0px",padding:"10px"}}>{message.text} </p>
          </div>
        )
    }
    return (
      <div style={{textAlign:"left", margin:"10px",marginLeft:"15%", marginRight:"auto",background:'#d9dadb',  position: "relative",width: "300px", height: "auto" , borderRadius: "30px", padding:"10px"}}>
        <p key={index} className="message" style={{margin:"0px",padding:"10px"}}>{message.text} </p>
      </div>
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
