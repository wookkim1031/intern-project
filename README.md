# Sales Strategy Optimization

This project focuses on optimizing sales strategy through data-driven insights and machine learning models. The goal is to assist workers in making informed decisions about marketing, inventory management, and sales patterns across different countries. This application includes interactive dashboards, machine learning predictions, and solutions to address deployment challenges.

---

## Use Cases

### Marketing Optimization
- Identify which product need additional marketing efforts based on their value and sales trends.

### Inventory Management
- Determine which product should be stored in larger quantities in specific countries to meet demand.

### Product Insights
- Understand which product are the most popular in different countries.
- Analyze sales trends of specific models during different time periods.

### Seasonal Sales
- Detect seasonal trends to help optimize marketing campaigns and inventory planning.

### Machine Learning Predictions
- Predict which product are likely to sell the most in specific countries, enabling proactive decision-making.

---

## Challenges and Solutions

### Deployment Challenges
- **Large Datasets**:
  - Perform server-side aggregation to reduce data volume.
  - Optimize queries to fetch only essential data.
  - Implement client-side caching using React hooks (`useMemo` and `useCallback`).

- **Real-Time Interaction**:
  - Use caching strategies to enhance data retrieval speed.
  - Implement lazy loading and pagination to handle large datasets efficiently.

- **Security Concerns**:
  - Utilize role-based access to restrict sensitive data access.
  - Leverage BMW’s internal security measures for additional protection.

- **Docker and Kubernetes**:
  - Containerize the application with Docker, ensuring each container has isolated dependencies.
  - Use Kubernetes for orchestrating containers, enabling scalability and fault tolerance.

### Integration Challenges
- **Connecting APIs**:
  - Investigate BMW’s internal APIs, repositories, and artifactory systems for data integration.
  - Assess restrictions on external services such as ChatGPT, Copilot, and Hugging Face.
  - Use pattern-based recognition for dates, categories, and other entities when external tools are restricted.

---

## Key Features

- **Interactive Dashboards**:
  - Visualize sales, product trends, and seasonal patterns.
  - Filter data by date, country, product, and other categories.

- **Role-Based Access Control**:
  - Assign roles (e.g., managers, analysts, executives) to restrict visibility based on stakeholders’ needs.

- **NLP Query Processing**:
  - Enable natural language input for intuitive queries (e.g., *"Show the top 5 products sold in Germany last quarter"*).
  - Implement confidence scoring for NLP-based queries to ensure accuracy.
  - Cache query results to improve performance.

- **Machine Learning Predictions**:
  - Predict the top-selling products in specific countries using advanced ML algorithms.

---

## Proposed Solutions

### Data Processing
- Aggregate data to generate pre-computed metrics for faster queries.
- Cache frequently accessed data to reduce database load.

### Front-End Optimization
- Use React hooks (`useMemo`, `useCallback`) to optimize component rendering.
- Implement client-side pagination and lazy loading for smooth interactions.

### Backend Architecture
- Use Docker for containerization to ensure consistent environments.
- Deploy with Kubernetes for scalability and fault tolerance.

### API Integration
- Identify and integrate BMW’s internal APIs for data retrieval.
- Explore using Hugging Face for NLP tasks (if not restricted).

---

## Future Enhancements

- Strengthen security measures for protecting sensitive data.
- Extend machine learning models to predict long-term market trends and customer demands.
- Implement real-time dashboards with live data streaming for more immediate decision-making.

---

## Conclusion

This project delivers a robust solution for optimizing BMW’s sales strategy by combining data analytics, machine learning, and scalable deployment strategies. By focusing on key use cases, stakeholder needs, and deployment challenges, this system empowers BMW to make data-driven decisions for long-term success.

---

## How to Run

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/bmw-sales-strategy.git
   cd bmw-sales-strategy

---

# Thoughts of Task 2




---

# Thoughts of Task 3

Natural Language Integration for Dashboard Interaction 

- Hugging face is popular model with large community and „easy“ way to use various transformer models (other option: TensorFlow Hub) 
    - Research Institution: Meta AI, Google AI 
- Hugging face good for the institution, because only need to download once
- Use GCP (using VERTEX AI or Cloud Run) to host hugging face model
    - Ex. S
    - DeepSeek-R1 (can not be fined tuned but a massive LLM model)
        - Transformer can be downloaded on HuggingFace
        - Downside Huge Hardware Requirements (16GB+) and Memory Usage
        - Security not proven 
    - https://huggingface.co/billatsectorflow/stella_en_1.5B_v5?language=python (https://huggingface.co/spaces/mteb/leaderboard) 
        - Least GPU used. 
        - In such task which not a lot of people use. Huge model is unnecessary
    - For large audience 
        - Lima, Gemini,
            - Security of data leakage very important
- Beside the project, run centralised evaluation and visualisations results
    - Evaluate the model using open source project: mlCheck and LLMEval
- Fine tune hugging face models on GCP 
    1. Feeding more data onto the the datasets covering diverse tasks and domains
    2. Encourage coworkers to work and evaluate the data because I can not do it alone 
    * With VERTEX AI, Leverage TPUs/GPUs on GCP for efficient fine-tuning of Hugging Face models.
- Evaluate the model comprehensively 
    - Define its strength and limitations 
    - Resource Requirements: computational availability in BMW 
    - Compare LLM models use to test the datasets and see which model is the most suitable one
- Docker and Kubernetes: 
    - Create a central artifactory repository to store and approve the data. Docker brings along the benefit of wide use and version control 
    - Helps with vulnerability check. Whether the Model meets the security requirements from BMW
    * Central Artifactory Repository:
        * Store models and datasets securely.
        * Approve versions before deployment
- Give access control 
    - Important to authorise users that should be allowed to use the program 
- Last step: monitoring 
    - Monitor how the model is working 
    - Version control: when the improvements are needed. Need a pipeline which can update the model continuously throughout the Quartal. 

- Integrate the model with the Dashboard
    - With the use of APIs 
- * Warning a lot of „POST“ testing required to fine tune. (POSTMAN tool)


- Step 1: User Interaction
    - 1. Propose custom question textarea
    - 2. Propose recommended frequent asked questions (Prompt engineering use prompts to answer the questions) 
- Step 2: Divide into Recommended prompt or frequent asked questions
- Step 3: Invoke LLM Analysis (can use GCP model or hugging face model) but need to find an appropriate model 
- Step 4: Maintaining the history in order to improve and fine tune the model. 
