CREATE DATABASE IF NOT EXISTS hospital_patient_manager CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE hospital_patient_manager;

CREATE TABLE Patients (
    PatientID INT PRIMARY KEY AUTO_INCREMENT,
    PatientName VARCHAR(255) NOT NULL,
    Birthdate DATE NULL
);

CREATE TABLE Doctors (
    DoctorID INT PRIMARY KEY AUTO_INCREMENT,
    DoctorName VARCHAR(255) NOT NULL,
    Specialty VARCHAR(255) NULL
);

CREATE TABLE Treatments (
    TreatmentID INT PRIMARY KEY AUTO_INCREMENT,
    TreatmentName VARCHAR(255) NOT NULL UNIQUE,
    StandardCost DECIMAL(10, 2) NOT NULL
);

CREATE TABLE TreatmentSessions (
    SessionID INT PRIMARY KEY AUTO_INCREMENT,
    PatientID INT NOT NULL,
    DoctorID INT NOT NULL,
    TreatmentID INT NOT NULL,
    TreatmentDate DATETIME NOT NULL,

    CONSTRAINT fk_patient FOREIGN KEY (PatientID) REFERENCES Patients(PatientID),
    CONSTRAINT fk_doctor FOREIGN KEY (DoctorID) REFERENCES Doctors(DoctorID),
    CONSTRAINT fk_treatment FOREIGN KEY (TreatmentID) REFERENCES Treatments(TreatmentID)
);

CREATE INDEX idx_session_patient ON TreatmentSessions(PatientID);
CREATE INDEX idx_session_doctor ON TreatmentSessions(DoctorID);
CREATE INDEX idx_session_treatment ON TreatmentSessions(TreatmentID);
CREATE INDEX idx_session_date ON TreatmentSessions(TreatmentDate);

