const mongoose = require('mongoose');

const dbURI = 'mongodb://localhost:27017/booking_events';  // Local MongoDB URI

// Only call mongoose.connect if it's not already connected
if (mongoose.connection.readyState === 0) {
    mongoose.connect(dbURI)
    .then(() => {
        console.log('MongoDB connected successfully');
    })
    .catch((err) => {
        console.error('MongoDB connection error:', err);
        process.exit(1); // Exit the process if connection fails
    });
} else {
    console.log('MongoDB is already connected');
}

module.exports = mongoose;  // Export mongoose for use in other files
