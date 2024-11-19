import React, {useState} from 'react';
import LoginForm from '../components/LoginForm';

function LoginContainer () {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState(null);
    const [message, setMessage] = useState(null);

    const handleLogin = async () => {
        try {
            //LOOK HERE: May need URL change
            const response = await fetch('http://127.0.0.1:5001/api/mobile_login',{
                method: 'POST',
                headers: {
                    'Content-Type': 'applications/json',
                },
                body: JSON.stringify({
                    username: username,
                    password: password,
                }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                setError(errorData.error);
                return;
            }

            // Get data from response
            const data = await response.json();

            // Handle if the log in was a success
            setMessage(data.message);
            console.log('User ID:', data.user_id);
        } catch (err) {
            console.error('Login failed:', err);
            setError('Something went wrong, please try again later');
        }
    }
    return (
        <LoginForm 
            username={username} 
            setUsername={setUsername} 
            password={password} 
            setPassword={setPassword}
            handleLogin={handleLogin}></LoginForm>
    );
}

export default LoginContainer;