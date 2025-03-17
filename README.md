# Classroom Management System

[![Django](https://img.shields.io/badge/Django-3.2+-green.svg)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/DRF-3.12+-red.svg)](https://www.django-rest-framework.org/)
[![Postgres](https://img.shields.io/badge/PostgreSQL-13+-blue.svg)](https://www.postgresql.org/)
[![Kafka](https://img.shields.io/badge/Kafka-3.0+-orange.svg)](https://kafka.apache.org/)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-1.20+-326CE5.svg)](https://kubernetes.io/)
[![Nginx](https://img.shields.io/badge/Nginx-1.20+-009639.svg)](https://nginx.org/)
[![ElasticSearch](https://img.shields.io/badge/Elasticsearch-7.10+-005571.svg)](https://www.elastic.co/)
[![Docker](https://img.shields.io/badge/Docker-20.10+-2496ED.svg)](https://www.docker.com/)

A robust, scalable classroom management application built with Django REST Framework, Kafka, and PostgreSQL, Nginx, Docker and Kubernetes. 
This system allows educators to create quizzes, students to take them, and provides real-time analytics through an event-driven architecture.
The teachers can also create assignment and students can upload their answers for it within the deadline.Assignments can be assigned to sections


![Architecture Diagram](https://github.com/user-attachments/assets/339614cb-9560-4bb5-9184-dde836f29de3)

## ✨ Features

- **Quiz Creation and Management**: Create, update, and manage quizzes with various question types
- **Student Assignment**: Assign quizzes to individual students or groups
- **Real-time Results**: Process quiz submissions in real-time with Apache Kafka
- **Comprehensive Analytics**: Track student performance and quiz statistics
- **Advanced Search**: Find study materials with Elasticsearch fuzzy search
- **RESTful API**: Well-documented API for integration with other systems
- **Containerized Setup**: Easy deployment with Docker Compose or Kubernetes
- **High Performance**: Optimized with Nginx and uWSGI for production environments
- **Scalable Architecture**: Horizontally scalable with Kubernetes orchestration

## 🏗 Architecture

The application follows a modern microservices-inspired architecture with the following components:

### System Architecture
![Architecture Diagram](https://github.com/user-attachments/assets/339614cb-9560-4bb5-9184-dde836f29de3)

### Database Schema
![db schema 1](https://github.com/user-attachments/assets/9ad96835-fd63-4e75-99dc-161e3854ed7e)
![dbscehma 2](https://github.com/user-attachments/assets/ab3477fb-8683-44cf-8135-ee5892837925)

### Kafka Event Stream Architecture
![Kafka Architecture](https://github.com/user-attachments/assets/0f04d3a0-c006-4a9c-b0bb-062ce0960b48)



## 🔧 Tech Stack

### Backend
- **Django**: Web framework
- **Django REST Framework**: API development
- **uWSGI**: Application server
- **PostgreSQL**: Primary database
- **Redis**: Caching and task queue

### DevOps & Infrastructure
- **Docker**: Containerization
- **Kubernetes**: Container orchestration
- **Nginx**: Web server and reverse proxy


### Messaging & Search
- **Apache Kafka**: Event streaming platform
- **Zookeeper**: Kafka coordination
- **Elasticsearch**: Searchengine

### Monitoring & Documentation
- **DRF Spectacular**: API documentation with Swagger UI
- **Kafka UI**: Kafka management interface
- **Adminer**: Database administration

## 📚 API Documentation

The API is fully documented using DRF Spectacular, which provides interactive Swagger documentation:

![API Overview](https://github.com/user-attachments/assets/4c34ef6c-ef81-4da7-b521-a2febfb92143)
![image2](https://github.com/user-attachments/assets/7137dc04-1dbe-49e9-8559-010cd27e0318)
![image3](https://github.com/user-attachments/assets/863a3787-71c9-490d-a4b2-780819783997)
![image4](https://github.com/user-attachments/assets/1eb004c6-c869-426d-9bc1-a629c5d39bed)
![image5](https://github.com/user-attachments/assets/7ecd214a-ef83-4d26-a09b-658c3578af5e)

Access the interactive documentation at `/api/schema/swagger-ui/` when the application is running.

## 🚀 Installation

### Prerequisites

- Docker and Docker Compose (for local development)
- Kubectl and Kubernetes cluster (for production deployment)
- Git

### Docker Compose Setup

1. Clone the repository
   ```bash
   git clone https://github.com/your-username/quiz-management-system.git
   cd quiz-management-system
