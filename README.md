# How it works

* User first logs in using their username and password.
* The authentification service verifies the user's credentials and returns a JWT.
* Authenticated users are able to access all of the application's functionalities such as upload and download endpoints.
* Users receive an email to notify them of completion and includes the download ID.

# Architecture Overview

* The application makes use of microservices deployed on a Kubernetes cluster. (authentification, converter, queuing & notification)
  
* **Microservices**: A microservice architecture was chosen for its scalability, maintainability, and flexibility. By breaking down the application into smaller, independent services, it becomes easier to develop, deploy, and manage each component separately. This architecture also allows for better fault isolation and enables teams to work on different services concurrently. Decoupling also allows for individual scaling of services so that intensive workloads can be scaled accordingly.
  
* **Kubernetes**: Kubernetes was chosen as the container orchestration platform due to its range of features for automating deployment, scaling, and management of containerized applications. Kubernetes provides resilience through its self-healing capabilities. It continuously monitors the health of application components and automatically restarts or reschedules containers that fail or become unresponsive. Kubernetes also supports rolling updates and can dynamically adjust resource allocations to handle varying workloads, ensuring high availability and reliability.
  
* **RabbitMQ**: RabbitMQ queues are used to decouple the individual services. By setting up services to consume messages and publish messages to queues when completed, RabbitMQ is able to provide and facilitate asynchronous communication, allowing them to operate independently and asynchronously. Persistent queues and messages ensures that messages are not lost during system failures or restarts, and message acknowledgments enable services to confirm the successful processing of messages. This ensures message integrity and reliability, even in the event of failures or errors during message processing.
  
* **Databases**: User accounts are stored and verified using a MySQL database and uploaded videos (to be converted) and finished mp3 files are stored on MongoDB databases

# Optimizations and Improvements

* Currently, the MySQL and MongoDB databases are hosted locally with no backup and disaster recovery. Resiliency, fault tolerance, and high availability could be enhanced by implementing database backups and failover routing.
  
* Implement observability into the application. Better observability allows for easier troubleshooting, tracking performance through metrics, capacity planning and resource allocation, creating a more resilient system for better overall performance and user experience.
  
# System Architecture Diagram
![mp3converterdiagram drawio](https://github.com/tuning-ware/microservices-mp3-converter/assets/141936120/c8e5fcc1-2fd8-44b2-b168-40097a1df9e4)

# Acknowledgements

* Thank you Kantan Coding for this amazing tutorial and project!
* https://www.youtube.com/@kantancoding
