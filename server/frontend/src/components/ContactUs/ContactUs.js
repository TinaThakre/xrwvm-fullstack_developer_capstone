import React from 'react';
import Header from '../Header/Header';

const ContactUs = () => {
    return (
        <div>
            <Header />
            <div style={{ padding: '20px' }}>
                <h1>Contact Us</h1>
                <p>
                    We'd love to hear from you! Please reach out to us using the information below.
                </p>
                <ul>
                    <li>Email: contact@bestcars.com</li>
                    <li>Phone: (555) 123-4567</li>
                    <li>Address: 123 Dealership Drive, Auto City, USA</li>
                </ul>
            </div>
        </div>
    );
};

export default ContactUs;