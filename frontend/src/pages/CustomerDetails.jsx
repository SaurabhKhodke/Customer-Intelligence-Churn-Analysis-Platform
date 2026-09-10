import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { User, Activity, MapPin, Calendar, CreditCard, ShoppingBag, BrainCircuit, ArrowUpRight, ArrowDownRight } from 'lucide-react';
import { getCustomer, getCustomerExplanation } from '../services/api';
import RiskBadge from '../components/RiskBadge';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';

const CustomerDetails = () => {
  const { customerId } = useParams();
  const [customer, setCustomer] = useState(null);
  const [explanation, setExplanation] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        const [custData, explData] = await Promise.all([
          getCustomer(customerId),
          getCustomerExplanation(customerId).catch(() => null) // May not have explanation
        ]);
        setCustomer(custData);
        setExplanation(explData);
      } catch (err) {
        if (err.response && err.response.status === 404) {
          setError('Customer not found.');
        } else {
          setError(err.message || 'Failed to fetch customer details.');
        }
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [customerId]);

  if (loading) return <LoadingSpinner />;
  if (error) return <ErrorMessage message={error} />;
  if (!customer) return null;

  return (
    <div style={{ paddingBottom: '2rem' }}>
      <div className="flex justify-between items-center mb-4">
        <div>
          <h1 style={{ fontSize: '1.5rem', marginBottom: '0.25rem' }}>Customer Profile: #{customer.customer_id}</h1>
          <div className="text-muted flex items-center gap-2">
            <MapPin size={14} /> {customer.city}
          </div>
        </div>
        <div style={{ textAlign: 'right' }}>
          <div className="text-muted" style={{ fontSize: '0.85rem', marginBottom: '0.25rem' }}>Churn Risk</div>
          <RiskBadge risk={customer.risk || 'UNKNOWN'} />
          {customer.churn_probability !== undefined && (
            <div style={{ fontWeight: 600, marginTop: '0.25rem' }}>
              {(customer.churn_probability * 100).toFixed(1)}% Probability
            </div>
          )}
        </div>
      </div>

      <div className="grid-cols-2 mb-4">
        <div className="card mb-0">
          <h3 className="card-title border-bottom pb-2 mb-3">Demographics & Account</h3>
          <div className="grid-cols-2 gap-4">
            <div>
              <div className="text-muted mb-1" style={{ fontSize: '0.8rem' }}>Age</div>
              <div style={{ fontWeight: 500 }}>{customer.age} years</div>
            </div>
            <div>
              <div className="text-muted mb-1" style={{ fontSize: '0.8rem' }}>Gender</div>
              <div style={{ fontWeight: 500 }}>{customer.gender}</div>
            </div>
            <div>
              <div className="text-muted mb-1" style={{ fontSize: '0.8rem' }}>Tenure</div>
              <div style={{ fontWeight: 500 }}>{customer.tenure_months} months</div>
            </div>
            <div>
              <div className="text-muted mb-1" style={{ fontSize: '0.8rem' }}>Acquisition Channel</div>
              <div style={{ fontWeight: 500 }}>{customer.acquisition_channel}</div>
            </div>
            <div>
              <div className="text-muted mb-1" style={{ fontSize: '0.8rem' }}>Subscription Plan</div>
              <div style={{ fontWeight: 500 }}>{customer.subscription_plan}</div>
            </div>
            <div>
              <div className="text-muted mb-1" style={{ fontSize: '0.8rem' }}>Payment Method</div>
              <div style={{ fontWeight: 500 }}>{customer.payment_method}</div>
            </div>
          </div>
        </div>

        <div className="card mb-0">
          <h3 className="card-title border-bottom pb-2 mb-3">Behavior & Engagement</h3>
          <div className="grid-cols-2 gap-4">
            <div>
              <div className="text-muted mb-1" style={{ fontSize: '0.8rem' }}>Total Orders</div>
              <div style={{ fontWeight: 500 }}>{customer.orders_count}</div>
            </div>
            <div>
              <div className="text-muted mb-1" style={{ fontSize: '0.8rem' }}>Monthly Spend</div>
              <div style={{ fontWeight: 500 }}>${customer.monthly_spend?.toFixed(2)}</div>
            </div>
            <div>
              <div className="text-muted mb-1" style={{ fontSize: '0.8rem' }}>Recency</div>
              <div style={{ fontWeight: 500 }}>{customer.recency_days} days ago</div>
            </div>
            <div>
              <div className="text-muted mb-1" style={{ fontSize: '0.8rem' }}>Satisfaction Score</div>
              <div style={{ fontWeight: 500 }}>{customer.satisfaction_score} / 5</div>
            </div>
            <div>
              <div className="text-muted mb-1" style={{ fontSize: '0.8rem' }}>Support Tickets</div>
              <div style={{ fontWeight: 500 }}>{customer.support_tickets}</div>
            </div>
            <div>
              <div className="text-muted mb-1" style={{ fontSize: '0.8rem' }}>Discount Usage</div>
              <div style={{ fontWeight: 500 }}>{(customer.discount_usage_rate * 100).toFixed(0)}%</div>
            </div>
          </div>
        </div>
      </div>

      <div className="card mb-4">
        <h3 className="card-title">Why is this customer at risk? (SHAP Explanation)</h3>
        {!explanation ? (
          <div className="text-muted">No explanation available for this customer.</div>
        ) : (
          <div className="table-container mt-3">
            <table>
              <thead>
                <tr>
                  <th>Factor (Feature)</th>
                  <th>Value</th>
                  <th>Impact (SHAP)</th>
                  <th>Effect on Churn</th>
                </tr>
              </thead>
              <tbody>
                {explanation.top_factors.map((factor, idx) => {
                  const isPositiveImpact = factor.direction === 'increases churn risk';
                  return (
                  <tr key={idx}>
                    <td style={{ fontWeight: 500 }}>{factor.feature}</td>
                    <td>{factor.value}</td>
                    <td>
                      <span style={{ 
                        color: isPositiveImpact ? '#b91c1c' : '#15803d',
                        fontWeight: 600,
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.25rem'
                      }}>
                        {isPositiveImpact ? <ArrowUpRight size={14} /> : <ArrowDownRight size={14} />}
                        {factor.shap_value > 0 ? '+' : ''}{factor.shap_value}
                      </span>
                    </td>
                    <td>
                      <span className="text-muted">
                        {factor.direction.charAt(0).toUpperCase() + factor.direction.slice(1)}
                      </span>
                    </td>
                  </tr>
                )})}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <div className="card bg-main border-primary" style={{ backgroundColor: '#f0fdfa', borderColor: '#5eead4' }}>
        <div className="flex items-center gap-2 mb-2">
          <BrainCircuit size={20} style={{ color: '#0f766e' }} />
          <h3 className="card-title" style={{ margin: 0, color: '#0f766e' }}>AI Customer Insight</h3>
        </div>
        <p style={{ color: '#115e59', fontSize: '0.9rem' }}>
          AI-powered customer recommendations and conversational insights.
        </p>
        <Link to="/ai-insights" className="btn mt-3" style={{ backgroundColor: '#0d9488', color: 'white', fontSize: '0.8rem' }}>
          Explore AI Tools
        </Link>
      </div>
    </div>
  );
};

export default CustomerDetails;
