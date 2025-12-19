import React, { useState, useEffect } from 'react';
import { Upload, FileText, CreditCard, Calendar, DollarSign, Hash, AlertCircle, CheckCircle, Download, Activity } from 'lucide-react';
import './App.css';

function App() {
  const [file, setFile] = useState(null);
  const [extractedData, setExtractedData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const API_URL = 'http://localhost:5000/api';

  const handleFileUpload = async (e) => {
    const uploadedFile = e.target.files[0];
    if (!uploadedFile) return;

    if (uploadedFile.type !== 'application/pdf') {
      setError('Please upload a PDF file');
      return;
    }

    setFile(uploadedFile);
    setError(null);
    setLoading(true);
    setExtractedData(null);

    try {
      const formData = new FormData();
      formData.append('file', uploadedFile);

      const response = await fetch(`${API_URL}/parse`, {
        method: 'POST',
        body: formData,
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.error || 'Failed to parse PDF');
      }

      if (result.success && result.data) {
        setExtractedData(result.data);
      } else {
        throw new Error('No data extracted from PDF');
      }

      setLoading(false);
    } catch (err) {
      setError(err.message || 'Error parsing PDF. Please try another file.');
      setLoading(false);
    }
  };

  const downloadResults = () => {
    if (!extractedData) return;
    
    const dataStr = JSON.stringify(extractedData, null, 2);
    const blob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `statement_${extractedData.last_four_digits || Date.now()}.json`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const DataField = ({ icon: Icon, label, value, highlight = false }) => (
    <div className={`data-field ${highlight ? 'highlight' : ''}`}>
      <div className="field-header">
        <Icon size={18} />
        <span className="field-label">{label}</span>
      </div>
      <div className="field-value">{value || 'Not found'}</div>
    </div>
  );

  return (
    <div className="app-container">
      <div className="app-content">
        {/* Header */}
        <header className="app-header">
          <div className="header-title">
            <Activity size={32} strokeWidth={2.5} />
            <div>
              <h1>Credit Card Statement Parser</h1>
              <p className="subtitle">Automated data extraction from PDF statements</p>
            </div>
          </div>
          
          <div className="supported-banks">
            Supports: HDFC • ICICI • SBI • Axis • Kotak
          </div>
        </header>

        <div className="main-content">
          {/* Upload Section */}
          {!extractedData && (
            <div className="upload-section">
              <div className="upload-card">
                <label className="upload-area active">
                  <input
                    type="file"
                    accept=".pdf"
                    onChange={handleFileUpload}
                  />
                  <div className="upload-content">
                    <Upload size={48} strokeWidth={1.5} />
                    <div className="upload-text">
                      <h3>{file ? file.name : 'Select PDF Statement'}</h3>
                      <p>Click to browse or drag and drop your file here</p>
                    </div>
                  </div>
                </label>

                <div className="upload-info">
                  <div className="info-item">
                    <CheckCircle size={16} />
                    <span>Supports digital PDF statements</span>
                  </div>
                  <div className="info-item">
                    <CheckCircle size={16} />
                    <span>Extracts 5 key data points automatically</span>
                  </div>
                  <div className="info-item">
                    <CheckCircle size={16} />
                    <span>All processing done locally</span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Loading State */}
          {loading && (
            <div className="status-card loading">
              <div className="spinner"></div>
              <h3>Processing Statement</h3>
              <p>Extracting data from your PDF file...</p>
            </div>
          )}

          {/* Error State */}
          {error && (
            <div className="status-card error">
              <AlertCircle size={48} />
              <h3>Processing Failed</h3>
              <p>{error}</p>
              <button className="btn-secondary" onClick={() => setError(null)}>
                Try Again
              </button>
            </div>
          )}

          {/* Results */}
          {extractedData && !loading && (
            <div className="results-section">
              <div className="results-header">
                <div>
                  <h2>Extracted Data</h2>
                  <p className="results-subtitle">Successfully parsed statement information</p>
                </div>
                <div className="results-actions">
                  <button className="btn-secondary" onClick={() => {
                    setExtractedData(null);
                    setFile(null);
                    setError(null);
                  }}>
                    New Statement
                  </button>
                  <button className="btn-primary" onClick={downloadResults}>
                    <Download size={18} />
                    Export JSON
                  </button>
                </div>
              </div>

              <div className="data-grid">
                {/* Bank Info */}
                <div className="data-card bank-card">
                  <div className="card-icon">
                    <CreditCard size={24} />
                  </div>
                  <div className="card-content">
                    <h3>Card Issuer</h3>
                    <p className="bank-name">{extractedData.issuer}</p>
                  </div>
                </div>

                {/* Card Details */}
                <div className="data-section">
                  <h3 className="section-title">Card Information</h3>
                  <div className="fields-group">
                    <DataField 
                      icon={Hash} 
                      label="Card Number" 
                      value={extractedData.card_number} 
                    />
                    <DataField 
                      icon={Hash} 
                      label="Last 4 Digits" 
                      value={extractedData.last_four_digits} 
                    />
                  </div>
                </div>

                {/* Billing Info */}
                <div className="data-section">
                  <h3 className="section-title">Billing Details</h3>
                  <div className="fields-group">
                    <DataField 
                      icon={Calendar} 
                      label="Billing Cycle" 
                      value={extractedData.billing_cycle} 
                    />
                    <DataField 
                      icon={Calendar} 
                      label="Payment Due Date" 
                      value={extractedData.due_date}
                      highlight
                    />
                  </div>
                </div>

                {/* Amount Due */}
                <div className="data-card amount-card">
                  <div className="card-icon">
                    <DollarSign size={24} />
                  </div>
                  <div className="card-content">
                    <h3>Total Amount Due</h3>
                    <p className="amount">{extractedData.total_balance}</p>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;