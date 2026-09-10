import React, { useState } from 'react';
import { predict } from '../services/api';
import RiskBadge from '../components/RiskBadge';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';
import { BrainCircuit, ArrowUpRight, ArrowDownRight, Settings, Users, Activity, HeartHandshake } from 'lucide-react';
import Combobox from '../components/Combobox';

const Prediction = () => {
  const defaultState = {
    age: 35,
    gender: 'Male',
    city: 'Pune',
    acquisition_channel: 'Organic',
    subscription_plan: 'Basic',
    payment_method: 'Credit Card',
    tenure_months: 12,
    orders_count: 5,
    monthly_spend: 100.0,
    recency_days: 15,
    discount_usage_rate: 0.2,
    satisfaction_score: 4,
    support_tickets: 1,
    orders_per_month: 0.4,
    support_tickets_per_month: 0.1,
  };

  const [formData, setFormData] = useState(defaultState);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  const formatFeatureName = (name) => {
    const featureMap = {
      recency_days: 'Recency (Days)',
      orders_count: 'Total Orders',
      orders_per_month: 'Orders / Month',
      support_tickets: 'Support Tickets',
      support_tickets_per_month: 'Support Tickets / Month',
      satisfaction_score: 'Satisfaction Score',
      tenure_months: 'Tenure (Months)',
      monthly_spend: 'Monthly Spend',
      discount_usage_rate: 'Discount Usage Rate',
      age: 'Age',
      gender: 'Gender',
      city: 'City',
      acquisition_channel: 'Acquisition Channel',
      subscription_plan: 'Subscription Plan',
      payment_method: 'Payment Method',
    };
    return featureMap[name] || name.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
  };

  const loadPreset = (type) => {
    setResult(null);
    setError(null);
    if (type === 'low') {
      setFormData({
        age: 42,
        gender: 'Female',
        city: 'Mumbai',
        acquisition_channel: 'Organic',
        subscription_plan: 'Premium',
        payment_method: 'Credit Card',
        tenure_months: 36,
        orders_count: 45,
        monthly_spend: 250.0,
        recency_days: 5,
        discount_usage_rate: 0.1,
        satisfaction_score: 5,
        support_tickets: 0,
        orders_per_month: 1.25,
        support_tickets_per_month: 0,
      });
    } else if (type === 'medium') {
      setFormData({
        age: 28,
        gender: 'Male',
        city: 'Delhi',
        acquisition_channel: 'Paid Ads',
        subscription_plan: 'Standard',
        payment_method: 'UPI',
        tenure_months: 12,
        orders_count: 8,
        monthly_spend: 85.0,
        recency_days: 20,
        discount_usage_rate: 0.4,
        satisfaction_score: 3,
        support_tickets: 2,
        orders_per_month: 0.6,
        support_tickets_per_month: 0.15,
      });
    } else if (type === 'high') {
      setFormData({
        age: 35,
        gender: 'Male',
        city: 'Bangalore',
        acquisition_channel: 'Social Media',
        subscription_plan: 'Basic',
        payment_method: 'Debit Card',
        tenure_months: 2,
        orders_count: 1,
        monthly_spend: 15.0,
        recency_days: 45,
        discount_usage_rate: 0.8,
        satisfaction_score: 1,
        support_tickets: 4,
        orders_per_month: 0.5,
        support_tickets_per_month: 2.0,
      });
    }
  };

  const handleChange = (e) => {
    const { name, value, type } = e.target;
    let parsedValue = value;

    if (type === 'number' || type === 'range') {
      parsedValue = value === '' ? '' : Number(value);
    }

    setFormData(prev => ({
      ...prev,
      [name]: parsedValue
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const prediction = await predict(formData);
      setResult(prediction);
    } catch (err) {
      setError(err.message || 'Prediction failed. Please check inputs and try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="grid-cols-2" style={{ gridTemplateColumns: '1.2fr 0.8fr', gap: '2rem' }}>
      <div>
        <div className="flex justify-between items-center mb-4">
          <h1 style={{ fontSize: '1.5rem', margin: 0 }}>Run Churn Prediction</h1>
          <div className="flex gap-2">
            <button className="btn btn-outline" style={{ fontSize: '0.75rem', padding: '0.3rem 0.6rem' }} onClick={() => loadPreset('low')}>Load Low Risk Example</button>
            <button className="btn btn-outline" style={{ fontSize: '0.75rem', padding: '0.3rem 0.6rem' }} onClick={() => loadPreset('medium')}>Load Medium Risk Example</button>
            <button className="btn btn-outline" style={{ fontSize: '0.75rem', padding: '0.3rem 0.6rem' }} onClick={() => loadPreset('high')}>Load High Risk Example</button>
          </div>
        </div>

        <form onSubmit={handleSubmit}>
          {/* Customer Profile */}
          <div className="card mb-4">
            <h3 className="card-title mb-3 flex items-center gap-2 border-bottom pb-2">
              <Users size={16} className="text-muted" /> Customer Profile
            </h3>
            <div className="grid-cols-3 gap-3">
              <div className="form-group mb-0">
                <label className="form-label">Age</label>
                <input type="number" min="18" name="age" className="form-control" value={formData.age} onChange={handleChange} required />
              </div>
              <div className="form-group mb-0">
                <label className="form-label">Gender</label>
                <input type="text" list="genders" name="gender" className="form-control" value={formData.gender} onChange={handleChange} required />
                <datalist id="genders">
                  <option value="Male" />
                  <option value="Female" />
                  <option value="Other" />
                </datalist>
              </div>
              <div className="form-group mb-0">
                <label className="form-label">City</label>
                <Combobox
                  name="city"
                  value={formData.city}
                  onChange={handleChange}
                  options={['Mumbai', 'Delhi', 'Bangalore', 'Hyderabad', 'Chennai', 'Pune', 'Kolkata', 'Ahmedabad']}
                />
              </div>
            </div>
          </div>

          {/* Subscription & Acquisition */}
          <div className="card mb-4">
            <h3 className="card-title mb-3 flex items-center gap-2 border-bottom pb-2">
              <Settings size={16} className="text-muted" /> Subscription & Acquisition
            </h3>
            <div className="grid-cols-3 gap-3">
              <div className="form-group mb-0">
                <label className="form-label">Acquisition Channel</label>
                <Combobox
                  name="acquisition_channel"
                  value={formData.acquisition_channel}
                  onChange={handleChange}
                  options={['Organic', 'Paid Ads', 'Referral', 'Social Media', 'Email Campaign']}
                />
              </div>
              <div className="form-group mb-0">
                <label className="form-label">Subscription Plan</label>
                <Combobox
                  name="subscription_plan"
                  value={formData.subscription_plan}
                  onChange={handleChange}
                  options={['Basic', 'Standard', 'Premium']}
                />
              </div>
              <div className="form-group mb-0">
                <label className="form-label">Payment Method</label>
                <Combobox
                  name="payment_method"
                  value={formData.payment_method}
                  onChange={handleChange}
                  options={['UPI', 'Credit Card', 'Debit Card', 'Net Banking', 'Wallet']}
                />
              </div>
            </div>
          </div>

          {/* Customer Behavior */}
          <div className="card mb-4">
            <h3 className="card-title mb-3 flex items-center gap-2 border-bottom pb-2">
              <Activity size={16} className="text-muted" /> Customer Behavior
            </h3>
            <div className="grid-cols-3 gap-3" style={{ marginBottom: '1rem' }}>
              <div className="form-group mb-0">
                <label className="form-label">Tenure (Months)</label>
                <input type="number" min="0" name="tenure_months" className="form-control" value={formData.tenure_months} onChange={handleChange} required />
              </div>
              <div className="form-group mb-0">
                <label className="form-label">Total Orders</label>
                <input type="number" min="0" name="orders_count" className="form-control" value={formData.orders_count} onChange={handleChange} required />
              </div>
              <div className="form-group mb-0">
                <label className="form-label">Monthly Spend ($)</label>
                <input type="number" step="0.01" min="0" name="monthly_spend" className="form-control" value={formData.monthly_spend} onChange={handleChange} required />
              </div>
            </div>
            <div className="grid-cols-2 gap-3">
              <div className="form-group mb-0">
                <label className="form-label">Recency (Days)</label>
                <input type="number" min="0" name="recency_days" className="form-control" value={formData.recency_days} onChange={handleChange} required />
              </div>
              <div className="form-group mb-0">
                <label className="form-label">Orders / Month</label>
                <input type="number" step="0.01" min="0" name="orders_per_month" className="form-control" value={formData.orders_per_month} onChange={handleChange} required />
              </div>
            </div>
          </div>

          {/* Engagement & Support */}
          <div className="card mb-4">
            <h3 className="card-title mb-3 flex items-center gap-2 border-bottom pb-2">
              <HeartHandshake size={16} className="text-muted" /> Engagement & Support
            </h3>
            <div className="grid-cols-2 gap-3" style={{ marginBottom: '1rem' }}>
              <div className="form-group mb-0">
                <label className="form-label">Discount Usage Rate (0 to 1)</label>
                <input type="number" step="0.01" min="0" max="1" placeholder="e.g. 0.2 means 20%" name="discount_usage_rate" className="form-control" value={formData.discount_usage_rate} onChange={handleChange} required />
                <small className="text-muted" style={{ fontSize: '0.75rem' }}>0.2 means 20% usage</small>
              </div>
              <div className="form-group mb-0">
                <label className="form-label">Satisfaction Score ({formData.satisfaction_score})</label>
                <input type="range" min="1" max="5" name="satisfaction_score" style={{ width: '100%' }} value={formData.satisfaction_score} onChange={handleChange} required />
                <div className="flex justify-between text-muted" style={{ fontSize: '0.75rem' }}>
                  <span>1 (Poor)</span>
                  <span>5 (Great)</span>
                </div>
              </div>
            </div>
            <div className="grid-cols-2 gap-3">
              <div className="form-group mb-0">
                <label className="form-label">Support Tickets</label>
                <input type="number" min="0" name="support_tickets" className="form-control" value={formData.support_tickets} onChange={handleChange} required />
              </div>
              <div className="form-group mb-0">
                <label className="form-label">Tickets / Month</label>
                <input type="number" step="0.01" min="0" name="support_tickets_per_month" className="form-control" value={formData.support_tickets_per_month} onChange={handleChange} required />
              </div>
            </div>
          </div>

          <button type="submit" className="btn btn-primary w-full" disabled={loading} style={{ padding: '1rem', fontSize: '1rem' }}>
            {loading ? 'Running Prediction...' : 'Run Prediction'}
          </button>
        </form>
      </div>

      <div>
        <div style={{ position: 'sticky', top: '1rem' }}>

          {error && <ErrorMessage message={error} />}

          {/* Prediction Result */}
          <div className="card mb-4">
            <h2 className="card-title mb-4 border-bottom pb-2">Prediction Result</h2>

            {loading && <LoadingSpinner text="Running ML Model..." />}

            {!loading && !error && !result && (
              <div className="text-center text-muted" style={{ padding: '3rem 0' }}>
                Fill out the form and submit to see prediction results.
              </div>
            )}

            {result && !loading && (
              <div>
                <div className="text-muted mb-1" style={{ fontSize: '0.85rem', fontWeight: 600, textTransform: 'uppercase' }}>Churn Probability</div>
                <div style={{ fontSize: '2.5rem', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '0.5rem', lineHeight: 1 }}>
                  {(result.churn_probability * 100).toFixed(2)}%
                </div>
                <div className="mb-4 flex items-center gap-2">
                  <span className="text-muted" style={{ fontSize: '0.85rem' }}>Risk Level:</span> <RiskBadge risk={result.risk} />
                </div>

                <div style={{ backgroundColor: 'var(--bg-main)', padding: '1rem', borderRadius: 'var(--border-radius)', border: '1px solid var(--border-color)' }}>
                  <h4 style={{ margin: '0 0 0.5rem 0', fontSize: '0.9rem' }}>Model Assessment</h4>
                  <p className="text-muted" style={{ fontSize: '0.85rem', margin: 0 }}>
                    This customer currently has a {result.risk.toLowerCase()} predicted probability of churn.
                  </p>
                </div>
              </div>
            )}
          </div>

          {/* SHAP Explanation */}
          {result && result.top_factors && !loading && (
            <div className="card mb-4">
              <h2 className="card-title mb-4 border-bottom pb-2">Why did the model make this prediction?</h2>
              <div className="table-container">
                <table>
                  <thead>
                    <tr>
                      <th>Factor</th>
                      <th>Value</th>
                      <th>Impact</th>
                      <th>Effect</th>
                    </tr>
                  </thead>
                  <tbody>
                    {result.top_factors.map((factor, idx) => {
                      const isPositiveImpact = factor.direction === 'increases churn risk';
                      return (
                        <tr key={idx}>
                          <td style={{ fontWeight: 500, fontSize: '0.85rem' }}>{formatFeatureName(factor.feature)}</td>
                          <td style={{ fontSize: '0.85rem' }}>{factor.value}</td>
                          <td>
                            <span style={{
                              color: isPositiveImpact ? '#b91c1c' : '#15803d',
                              fontWeight: 600,
                              display: 'flex',
                              alignItems: 'center',
                              gap: '0.25rem',
                              fontSize: '0.85rem'
                            }}>
                              {isPositiveImpact ? <ArrowUpRight size={14} /> : <ArrowDownRight size={14} />}
                              {factor.shap_value > 0 ? '+' : ''}{factor.shap_value}
                            </span>
                          </td>
                          <td>
                            <span className="text-muted" style={{ fontSize: '0.85rem' }}>
                              {factor.direction.charAt(0).toUpperCase() + factor.direction.slice(1)}
                            </span>
                          </td>
                        </tr>
                      )
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* AI Insights Placeholder */}
          <div className="card bg-main border-primary" style={{ backgroundColor: '#f0fdfa', borderColor: '#5eead4' }}>
            <div className="flex items-center gap-2 mb-2">
              <BrainCircuit size={20} style={{ color: '#0f766e' }} />
              <h3 className="card-title" style={{ margin: 0, color: '#0f766e' }}>AI Insights</h3>
            </div>
            <p style={{ color: '#115e59', fontSize: '0.85rem', margin: 0 }}>
              Ask the AI assistant for a deeper explanation and recommended retention actions.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Prediction;
