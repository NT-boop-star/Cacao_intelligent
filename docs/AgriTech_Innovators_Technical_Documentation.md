# Technical Documentation Template

**Project Name:** Cacao Intelligent  
**Team Name:** AgriTech Innovators  
**Team Members:** [Insert Names]  
**Date:** March 16, 2026  

## 1. Executive Summary

Cacao Intelligent is an innovative IoT and AI-driven platform designed to optimize cocoa plantation management, specifically tailored for the environmental conditions of Abidjan, Côte d'Ivoire. The core problem we address is the lack of real-time datadriven decision-making in cocoa farming, compounded by the urgent need to comply with stringent environmental regulations such as the post-2020 EU deforestation-free regulation (EUDR). 

Our application's core value proposition lies in seamlessly integrating on-the-ground IoT sensors (ESP32) with advanced predictive AI models and global environmental databases. It empowers farmers with precise recommendations for irrigation, pesticide application, and disease detection (e.g., Blackpod) to maximize yield and minimize chemical overuse. Simultaneously, it automatically verifies land deforestation status via the Global Forest Watch API and generates rigorous Due Diligence Statements (DDS) as PDFs, ensuring complete end-to-end traceability of the supply chain via transparent QR codes.

## 2. User Stories

* **As a Cocoa Farmer**, I want to monitor microclimate data in real-time and receive AI-driven recommendations for irrigation and pesticides, so that I can optimize crop health and reduce resource waste.
* **As a Cooperative Manager / Exporter**, I want to automatically verify the non-deforestation status of cocoa parcels and generate Due Diligence Statements (DDS), so that I can easily maintain EUDR compliance for export.
* **As a Supply Chain Auditor / Consumer**, I want to scan a QR code attached to a cocoa batch, so that I can verify its entire journey (from collection to transit and export) and validate its geographical origin and sustainability.
* **As a Farmer**, I want to receive immediate SMS alerts about critical weather events or disease risks, so that I can take fast preventative action.

## 3. System Use Cases

* **Use Case Diagram:** [Insert Image/Link to Diagram]
* **Functional Descriptions:**
  * **User Authentication & Profile Management:** Secure login system allowing farmers, cooperatives, and auditors to access their specific dashboards and historical data. May integrate with MOSIP for secure, verifiable digital farmer identities.
  * **IoT Data Ingestion:** ESP32 sensors continuously push telemetry data (temperature, humidity, soil conditions) to the backend.
  * **AI Decision Support & Disease Detection:** Evaluation of environmental variables to recommend safe pesticide spraying or irrigation. Image analysis is used to detect pod abnormalities like Frostypod or Mirid damage.
  * **EUDR Compliance & DDS Generation:** System queries external APIs (Global Forest Watch) with parcel GPS coordinates to confirm zero deforestation post-2020, then compiles this into a legally viable Due Diligence PDF.
  * **QR Traceability Tracking:** The platform updates batch limits across distinct logistical states (Pending, Collected, In Transit, Exported) and links them to dynamic QR codes for public scanning.

## 4. System Architecture

* **Architecture Diagram:** [Insert High-Level Diagram: Frontend, Backend, Database, and any third-party APIs/MOSIP integrations]
* **Tech Stack:**
  * **Frontend:** Streamlit (Python) for a responsive, fast-to-iterate analytical dashboard.
  * **Backend:** Flask (Python) powering the core API, handling business logic, state management, and ML model inference.
  * **Database:** Local JSON-based object storage (`agriculteurs.json`) for lightweight profile, history, and lot tracking.
  * **Infrastructure:** Standard Python Virtual Environments (`venv`, `venv_tf`); suitable for future Dockerization and cloud deployment.
  * **AI & Machine Learning:** TensorFlow/Keras and scikit-learn for trained predictive models (`.h5`, `.pkl`).
  * **Third-Party APIs:** Twilio API (SMS Alerts), Global Forest Watch API (Environmental Verification), capability for MOSIP API (Digital Identity).

## 5. Data Model & Design

* **Entity Relationship Diagram (ERD):** [Insert Diagram showing database tables and relationships]
* **Key Tooling:** 
  * **Streamlit & Flask:** Rapid frontend-backend decoupling.
  * **ReportLab:** Dynamic generation of robust PDF documents for the DDS reports.
  * **TensorFlow / Keras:** For loading pre-trained deep learning models to perform complex image-based disease classification.
  * **Twilio SDK:** To dispatch asynchronous SMS alerts securely.
  * **QR Code Generation Libraries:** For encoding batch JSON representations mapping into verifiable supply chain points.
  * **Global Forest Watch API:** Providing critical geospatial verification for deforestation compliance.

---
**Submission Instructions Reminder:**
* **Save as:** AgriTech_Innovators_Technical_Documentation.pdf
* **Submit to:** blamptey@andrew.cmu.edu
* **Deadline:** Monday, March 16, 2026 (Hard Deadline)
