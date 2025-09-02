# Cloud-Based Audio Identification & Recommendation System

This project implements a cloud-based backend for identifying audio tracks and providing recommendations. It consists of multiple microservices that:

1. Receive and store audio files from users.
2. Identify tracks using the **Shazam API** and retrieve metadata via the **Spotify API**.
3. Generate personalized track recommendations.
4. Send results to users via email using **Mailgun**.

## Key Features
- Database (MySQL/PostgreSQL) for managing requests and their states (`pending`, `ready`, `done`, `failure`).
- Object Storage (S3-Compatible) for uploaded audio files.
- RabbitMQ for asynchronous service communication.
- Deployment-ready on AWS, Google Cloud, or Liara.

## Tech Stack
- **Backend:** Python  
- **Cloud Services:** AWS S3 / ArvanCloud, CloudAMQP, Mailgun  
- **APIs:** Shazam API, Spotify API  
- **Database:** MySQL/PostgreSQL  

