import React from 'react';

const Button = ({text, method}) => {
    return (
        <button onClick={method} className='btn'>{text}</button>
    );
};

export default Button;