# Fitness Telegram Bot

A comprehensive Telegram bot designed to help users track workouts, manage nutrition, and achieve their fitness goals through intelligent features and personalized recommendations.

## Overview

This fitness bot provides a complete workout tracking and management solution with features including exercise libraries, custom workout routines, nutrition tracking, workout timers, notifications, and detailed analytics. The bot is currently deployed in production as @kachialkabot.

## Core Features

### Exercise Library
Browse and search through a comprehensive database of exercises with detailed information. The library includes filtering options by muscle group, equipment type, and difficulty level. Users can navigate through exercises interactively and view complete descriptions and instructions for each movement.

### Workout Tracking
Log your workouts with detailed information including exercises, sets, reps, and weights. The system maintains a complete history of your training sessions, allowing you to track progress over time and review past workouts.

### Custom Workout Routines
Create and save personalized workout routines tailored to your specific goals and preferences. Build routines from the exercise library and access them quickly for your training sessions.

### Workout Timer
Built-in timer system with customizable presets for rest periods between sets. The timer uses a state machine architecture to manage different timer states and provides clear notifications when rest periods are complete.

### Nutrition Tracking
Monitor your daily caloric intake and macronutrient distribution. The nutrition feature includes BMR and TDEE calculators to help you determine your daily caloric needs based on your goals, whether bulking, cutting, or maintaining.

### Smart Notifications
Set up workout reminders and notifications to stay consistent with your training schedule. The notification system is fully customizable, allowing you to adjust training days and times to fit your schedule.

### Statistics & Analytics
Get insights into your training with detailed analytics including volume progression tracking, muscle group distribution analysis, and workout frequency statistics. The analytics help identify training patterns and potential imbalances in your routine.

### Workout Recommendations
Receive personalized exercise recommendations based on your training history and muscle group distribution to ensure balanced development and prevent overtraining specific areas.

### Multi-language Support
The bot includes translation capabilities to support users in different languages, making it accessible to a broader audience.

## Technical Architecture

The bot is built with a modular, feature-based architecture using Python and the Telegram Bot API. It uses SQLAlchemy for database management with a unified schema that integrates all features seamlessly. The application follows best practices with separated handlers, services, and data models for maintainability and scalability.

The project uses Docker for containerization and production deployment, ensuring consistent behavior across different environments. The FSM (Finite State Machine) pattern is implemented for complex user interactions like timer management and multi-step workout logging.

## Development Journey

The project evolved from a simple bot to a comprehensive fitness platform through iterative development. Starting with basic features like exercise databases and workout recommendations in late October 2025, the team progressively added nutrition tracking, timers, and notifications in early November.

A major architecture refactor in mid-November established the current modular structure with a unified database foundation, setting the stage for seamless integration of all features. The final weeks of November saw the integration of all components, production deployment, comprehensive documentation, and the addition of translation support in early December.

## Team

The project was developed collaboratively by a team of contributors, each focusing on different feature areas while maintaining architectural consistency across the codebase.
