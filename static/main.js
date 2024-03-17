import React from 'react';
import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';


let pc = new RTCPeerConnection();


async function createOffer() {

    // Fetch the offer from the server
    const offerResponse = await fetch("/offer", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            sdp: "",
            type: "offer",
        }),
    });

    // wait for response
    const offer = await offerResponse.json();

    // Set the remote description based on the received offer
    await pc.setRemoteDescription(new RTCSessionDescription(offer));

    // Create an answer and set it as the local description
    const answer = await pc.createAnswer();
    await pc.setLocalDescription(answer);
}



createOffer();