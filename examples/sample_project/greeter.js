// Sample JavaScript module for demonstration

class Greeter {
  constructor(name) {
    this.name = name;
  }
  
  greet() {
    return `Hello, ${this.name}!`;
  }
  
  farewell() {
    return `Goodbye, ${this.name}!`;
  }
}

function processArray(arr) {
  // Process an array of numbers
  return arr.map(x => x * 2)
            .filter(x => x > 10)
            .reduce((acc, x) => acc + x, 0);
}

const greeter = new Greeter("World");
console.log(greeter.greet());