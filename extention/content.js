

//
// SOCKET TO CONNECT WITH SERVER
//

var hightlightslow = 100    //Hz
// Establish WebSocket connection
var socket = new WebSocket('ws://localhost:8080');

var SELECT_ELEMENT_THRESHOLD = 0.6

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
function sendMessageToServer(content, urls, elementType, styles, borderX,borderY, check_selected) {
    if (socket.readyState === WebSocket.OPEN) {
        // Create a message object containing content, URL, and element type
        var message = {
            content: content,
            urls: urls,
            elementType: elementType,
            styles: styles,
            borderX: borderX,
            borderY:borderY,
            check_selected: check_selected,
            
        };

        // Convert the message object to JSON
        var jsonMessage = JSON.stringify(message);

        // Send the JSON message to the server
        socket.send(jsonMessage);
    } else {
        console.warn('WebSocket connection not open.');
    }
}


function getViewportFromScreenCoordinate(screenX, screenY){
    // Calculate the offset of the viewport relative to the screen
    var viewportOffsetX = window.screenLeft;
    var viewportOffsetY = window.screenTop;

    //The height and width of the browser tab and url bar
    var chromeHeight = window.outerHeight - window.innerHeight;
    var chromeWidth = window.outerWidth - window.innerWidth;

    // Adjust the screen coordinates by subtracting the viewport offset
    var viewportX = screenX - viewportOffsetX - chromeWidth;
    var viewportY = screenY - viewportOffsetY - chromeHeight;
    return { viewportX, viewportY };
}

function getElementFromScreenCoordinates(viewportX, viewportY) {
    
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
let canvas; // Global variable to hold the canvas reference
function drawCircle(viewportX, viewportY) {
    // Create a canvas element
    // If a canvas already exists, remove it
    if (canvas) {
        document.body.removeChild(canvas);
    }

    canvas = document.createElement('canvas');
    const context = canvas.getContext('2d');

    // Set the size of the canvas
    const circleRadius = 3; // Adjust the radius as needed
    canvas.width = circleRadius * 4;
    canvas.height = circleRadius * 4;

    // Set the position of the canvas
    canvas.style.position = 'fixed';
    canvas.style.left = `${viewportX - circleRadius}px`; // Center the circle
    canvas.style.top = `${viewportY - circleRadius}px`; // Center the circle
    canvas.style.pointerEvents = 'none'; // Make sure the canvas doesn't block clicks
    canvas.style.zIndex = 1000; // Ensure the canvas appears above other elements

    // Draw the circle
    context.beginPath();
    context.arc(circleRadius, circleRadius, circleRadius, 0, Math.PI * 2, false);
    context.fillStyle = 'red'; // Circle color
    context.fill();
    context.closePath();

    // Append the canvas to the body
    document.body.appendChild(canvas);
}


// Store a reference to the previously selected element
var previousElement = null;

var count = 0;
var selectedElement = null;

class Queue {
    constructor() {
        this.items = [];
    }

    enqueue(element) {
        this.items.push(element);
    }

    dequeue() {
        if (this.items.length > 0) {
            return this.items.shift();
        }
    }

    countOccurrences(element) {
        let count = 0;
        for (let i = 0; i < this.items.length; i++) {
            if (this.items[i] === element) {
                count++;
            }
        }
        return count;
    }
}

 
const queue = new Queue(); 
// Function to handle messages received from the WebSocket server
socket.onmessage = function(event) {
    // Parse the message received from the server
    var data = JSON.parse(event.data);

    // Extract the screenX and screenY coordinates from the message
    var screenX = data.gazeX;
    var screenY = data.gazeY;
	var { viewportX, viewportY } = getViewportFromScreenCoordinate(screenX, screenY)

    //drawCircle(viewportX, viewportY);

	// Get the element at the specified screen coordinates
    
    var element = getElementFromScreenCoordinates(viewportX, viewportY);

    
    
   var check_selected = 0;
	//sendMessageToServer(mappedX, mappedY, "");
    if (element) {
        // Remove outline from the previously selected element
        
        if (previousElement) {
            
            previousElement.style.border = '';
            
            // Apply highlight effect to the new element
            // if (count > hightlightslow){
            //     count = 0;
            //     selectedElement = element
            // }
            
            if (queue.items.length < 150) 
                {   
                    queue.enqueue(element)
                }
            else{
                queue.dequeue()
                queue.enqueue(element)
                count = queue.countOccurrences(element)
                if (count > 150*SELECT_ELEMENT_THRESHOLD) {
                    selectedElement = element  
                    check_selected = 1            
                }
                else{
                    selectedElement = null
                    check_selected = 0
    
                }
            }
            if (selectedElement){
                selectedElement.style.border = '2px solid red';
                
            }
            
            var content = element.innerText || element.textContent;

            // Get the type of element (tag name)
            var elementType = element.tagName.toLowerCase();
            
        
            // Get computed styles
            var computedStyles = window.getComputedStyle(element);
            var styles = {
                backgroundImage: computedStyles.getPropertyValue("background-image")
                };
            var borderX = element.getBoundingClientRect().left + window.screenLeft + (window.outerWidth - window.innerWidth);
            var borderY = element.getBoundingClientRect().top + window.screenTop + (chromeHeight = window.outerHeight - window.innerHeight);
            var urls = [];
        
            if (elementType === 'img') {
                urls.push(element.src);

                sendMessageToServer(element.alt, urls, elementType, styles, borderX,borderY,check_selected);    
            } 
            else if (elementType === 'a') {
                sendMessageToServer(content, element.href, elementType,styles, borderX,borderY,check_selected);
            } 
            else {
            
                    
                
                for (const child of element.children) {
                    if (child.tagName.toLowerCase() === "img"){
                        
                        urls.push(child.src)
                        }
                        
                    
                    
                }
                
                sendMessageToServer(content, urls, elementType, styles,borderX,borderY, check_selected);
            }
                
                
            
            
            // Update the reference to the previously selected element
            previousElement = element;
            
            
        }
          
        
        if (!previousElement)
        {
            
             // Get the content of the element
        var content = element.innerText || element.textContent;

        // Get the type of element (tag name)
        var elementType = element.tagName.toLowerCase();
    

       // Get computed styles
       var computedStyles = window.getComputedStyle(element);
       var styles = {
        backgroundImage: computedStyles.getPropertyValue("background-image")
         };
         var borderX = element.getBoundingClientRect().left + window.screenLeft + (window.outerWidth - window.innerWidth);
         var borderY = element.getBoundingClientRect().top + window.screenTop + (chromeHeight = window.outerHeight - window.innerHeight);

        // Send relevant information to the server
        if (elementType === 'img') {

          if (element.parentElement.tagName.toLowerCase() === 'p') {
             sendMessageToServer(element.parentElement.innerText, element.src, elementType + " " + element.parentElement.elementType,styles,borderX,borderY, check_selected);
          }
            sendMessageToServer(element.alt, element.src, elementType,styles,borderX,borderY, check_selected);    
        } 
        else if (elementType === 'a') {
            sendMessageToServer(content, element.href, elementType,styles, borderX,borderY, check_selected);
        } 
        else {
            if (element.querySelector('img')){
                sendMessageToServer(element.alt, element.querySelector('img').src, elementType, styles,borderX,borderY, check_selected);
            }
            
            sendMessageToServer(content, '', elementType, styles, borderX,borderY, check_selected);

        }

        // Apply highlight effect to the new element
        //element.style.outline = '2px solid red';
        }

        // Update the reference to the previously selected element
        previousElement = element;
    }
	else{
		sendMessageToServer("","","", "",screenX, screenY, "" );
	}
};

