//
// SOCKET TO CONNECT WITH SERVER
//

// Establish WebSocket connection
var socket = new WebSocket('ws://localhost:8080');

// Event: WebSocket connection opened
socket.onopen = function(event) {
    console.log('WebSocket connection opened.');
};

// Event: WebSocket error
socket.onerror = function(event) {
    console.error('WebSocket error:', event);
};

// Event: WebSocket connection closed
socket.onclose = function(event) {
    console.log('WebSocket connection closed.');
};

// Function to send message to WebSocket server
function sendMessageToServer(content, url, elementType, styles) {
    if (socket.readyState === WebSocket.OPEN) {
        // Create a message object containing content, URL, and element type
        var message = {
            content: content,
            url: url,
            elementType: elementType,
            styles: styles,
        };

        // Convert the message object to JSON
        var jsonMessage = JSON.stringify(message);

        // Send the JSON message to the server
        socket.send(jsonMessage);
    } else {
        console.warn('WebSocket connection not open.');
    }
}




function getElementFromScreenCoordinates(screenX, screenY) {
    // Calculate the offset of the viewport relative to the screen
    var viewportOffsetX = window.screenLeft;
    var viewportOffsetY = window.screenTop;
	
	//The height and width of the browser tab and url bar
	var chromeHeight = window.outerHeight - window.innerHeight;
    var chromeWidth = window.outerWidth - window.innerWidth;

    // Adjust the screen coordinates by subtracting the viewport offset
    var viewportX = screenX - viewportOffsetX - chromeWidth;
    var viewportY = screenY - viewportOffsetY - chromeHeight;

    // Use the adjusted coordinates to determine the element at that point
    var element = document.elementFromPoint(viewportX, viewportY);
	
	// Refine the result to return the topmost element
    //while (element && element.parentElement) {
    //    topElement = element;
    //    element = element.parentElement.elementFromPoint(viewportX, viewportY);
    //}
    
    //return topElement;
	return element
}

//
// HIGHTLIGHT AND EXTRACT ELEMENT CONTENT
//

/*
document.addEventListener('mousemove', function(event) {
	// Get the element at the cursor's position
	var element = getElementFromScreenCoordinates(event.screenX, event.screenY);

	// Get the content of the element
	var content = element.innerText || element.textContent;
	
	// Get the type of element (tag name)
	var elementType = element.tagName.toLowerCase();

	//Control if the element is div/img/anchor
	if (elementType === 'img') {
		sendMessageToServer(content, element.src, elementType);
	}
	else if (elementType === 'a'){
		sendMessageToServer(content, element.href, elementType);
	}
	else {
		sendMessageToServer(content, '', elementType);
	}
	
	// Apply highlight effect to the element
	element.style.outline = '2px solid red'; // Example highlight effect
	event.stopPropagation();
	
		// Add mouseout event listener
	document.addEventListener('mouseout', function(event) {

		// Remove highlight effect from the element
		element.style.outline = '';
		event.stopPropagation();
	});
		
});

*/


// Store a reference to the previously selected element
var previousElement = null;


// Function to handle messages received from the WebSocket server
socket.onmessage = function(event) {
    // Parse the message received from the server
    var data = JSON.parse(event.data);

    // Extract the screenX and screenY coordinates from the message
    var screenX = data.gazeX;
    var screenY = data.gazeY;
	
	// Get the element at the specified screen coordinates
    var element = getElementFromScreenCoordinates(screenX, screenY);
    // Get computed styles


	//sendMessageToServer(mappedX, mappedY, "");
    if (element) {
        // Remove outline from the previously selected element
        if (previousElement) {
            previousElement.style.outline = '';
        }
        

        // Get the content of the element
        var content = element.innerText || element.textContent;

        // Get the type of element (tag name)
        var elementType = element.tagName.toLowerCase();
       // Get computed styles
       var computedStyles = window.getComputedStyle(element);
       var styles = {
        backgroundImage: computedStyles.getPropertyValue("background-image")
         };
        // Send relevant information to the server
        if (elementType === 'img') {

          if (element.parentElement.tagName.toLowerCase() === 'p') {
            
            sendMessageToServer(element.parentElement.innerText, element.src, elementType + " " + element.parentElement,elementType);
          }
            sendMessageToServer(element.alt, element.src, elementType);
            
        } else if (elementType === 'a') {
            sendMessageToServer(content, element.href, elementType);
        } else {
            sendMessageToServer(content, '', elementType, styles);
        }

        // Apply highlight effect to the new element
        element.style.outline = '2px solid red';

        // Update the reference to the previously selected element
        previousElement = element;
    }
	else{
		sendMessageToServer(screenX, screenY, "");
	}
};
