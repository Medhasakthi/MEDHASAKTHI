import React from 'react';
import Head from 'next/head';

const HomePage: React.FC = () => {
  return (
    <>
      <Head>
        <title>MEDHASAKTHI - Student Portal</title>
        <meta name="description" content="MEDHASAKTHI Student Portal - Access your exams, results, and learning materials" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <main style={{ 
        minHeight: '100vh', 
        display: 'flex', 
        flexDirection: 'column', 
        alignItems: 'center', 
        justifyContent: 'center',
        padding: '2rem',
        fontFamily: 'system-ui, sans-serif'
      }}>
        <div style={{ textAlign: 'center', maxWidth: '600px' }}>
          <h1 style={{ 
            fontSize: '3rem', 
            marginBottom: '1rem', 
            color: '#2563eb',
            fontWeight: 'bold'
          }}>
            MEDHASAKTHI
          </h1>
          
          <h2 style={{ 
            fontSize: '1.5rem', 
            marginBottom: '2rem', 
            color: '#64748b'
          }}>
            Student Portal
          </h2>
          
          <p style={{ 
            fontSize: '1.1rem', 
            lineHeight: '1.6', 
            color: '#475569',
            marginBottom: '2rem'
          }}>
            Welcome to the MEDHASAKTHI Student Portal. Access your exams, view results, 
            and explore learning materials designed to help you excel in your educational journey.
          </p>
          
          <div style={{ 
            display: 'flex', 
            gap: '1rem', 
            justifyContent: 'center',
            flexWrap: 'wrap'
          }}>
            <button style={{
              padding: '0.75rem 1.5rem',
              backgroundColor: '#2563eb',
              color: 'white',
              border: 'none',
              borderRadius: '0.5rem',
              fontSize: '1rem',
              cursor: 'pointer',
              fontWeight: '500'
            }}>
              Login
            </button>
            
            <button style={{
              padding: '0.75rem 1.5rem',
              backgroundColor: 'transparent',
              color: '#2563eb',
              border: '2px solid #2563eb',
              borderRadius: '0.5rem',
              fontSize: '1rem',
              cursor: 'pointer',
              fontWeight: '500'
            }}>
              Register
            </button>
          </div>
        </div>
      </main>
    </>
  );
};

export default HomePage;
