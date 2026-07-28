import React from 'react';
import './Button.css'

const Button = ({text, method}) => {
    return (
        <button onClick={method} className='btn'>{text}</button>
    );
};

export default Button;