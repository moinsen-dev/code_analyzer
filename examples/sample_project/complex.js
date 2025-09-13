/**
 * A complex JavaScript file with various functions to test complexity analysis
 */

// A simple function
function simpleFunction() {
    return "Hello, World!";
}

// A complex function with many conditional paths
function complexFunction(a, b, c, d, e) {
    if (a && b) {
        if (c || d) {
            for (let i = 0; i < 10; i++) {
                if (i > 5) {
                    while (e > 0) {
                        e--;
                        if (e % 2 === 0) {
                            console.log("Even number");
                        } else {
                            console.log("Odd number");
                        }
                    }
                }
            }
        } else {
            switch (a) {
                case 1:
                    return "One";
                case 2:
                    return "Two";
                case 3:
                    return "Three";
                default:
                    return "Other";
            }
        }
    }
    return "Done";
}

// Another complex function with nested callbacks
function callbackHell() {
    setTimeout(() => {
        console.log("First timeout");
        setTimeout(() => {
            console.log("Second timeout");
            setTimeout(() => {
                console.log("Third timeout");
                setTimeout(() => {
                    console.log("Fourth timeout");
                    setTimeout(() => {
                        console.log("Fifth timeout");
                    }, 100);
                }, 100);
            }, 100);
        }, 100);
    }, 100);
}

// A class with complex methods
class ComplexClass {
    constructor() {
        this.data = [];
    }

    // A method with high cyclomatic complexity
    processData(items) {
        for (let i = 0; i < items.length; i++) {
            const item = items[i];
            if (item.type === "A") {
                if (item.value > 100) {
                    this.data.push({ processed: true, value: item.value * 2 });
                } else if (item.value > 50) {
                    this.data.push({ processed: true, value: item.value * 1.5 });
                } else {
                    this.data.push({ processed: false, value: item.value });
                }
            } else if (item.type === "B") {
                try {
                    const result = this.expensiveOperation(item);
                    this.data.push({ processed: true, value: result });
                } catch (error) {
                    console.error("Error processing item:", error);
                    this.data.push({ processed: false, value: 0 });
                }
            } else {
                this.data.push({ processed: false, value: item.value });
            }
        }
        return this.data;
    }

    expensiveOperation(item) {
        // Simulate expensive operation
        let result = 0;
        for (let i = 0; i < item.value; i++) {
            result += Math.sqrt(i);
        }
        return result;
    }
}

// Export for module use
module.exports = { simpleFunction, complexFunction, callbackHell, ComplexClass };