'use client';
import React, { useEffect } from 'react';
import ThreeDotLoader from '../Loader/ThreeDotLoader';
import { showCurrencySymbol } from '@/utils/common';
const UpcomingInvoice = ({ subscription, upcomingInvoice, upcomingInvoiceData, upcomingLoading }) => {
    useEffect(() => {
        upcomingInvoice();
    }, [subscription]);

    // Embedded CSS as a style object
    const tableStyles = {
        width: '100%',
        borderCollapse: 'collapse',
        margin: '20px 0',
        fontSize: '14px',
        textAlign: 'left',
    };

    const thStyles = {
        borderBottom: '2px solid #ddd',
        padding: '10px',
        backgroundColor: '#f2f2f2',
    };

    const tdStyles = {
        borderBottom: '1px solid #ddd',
        padding: '10px',
        backgroundColor: '#fff',
    };

    const rowStyles = {
        backgroundColor: '#f9f9f9',
    };

    const hoverStyles = {
        ':hover': {
            backgroundColor: '#f1f1f1',
        },
    };

    const summaryContainerStyles = {
        marginTop: '20px',
        textAlign: 'right', // Aligns content to the right
    };

    const formatDate = (timestamp) => {
        return new Date(timestamp * 1000).toLocaleDateString('en-GB', {
          day: '2-digit',
          month: 'short',
          year: 'numeric',
        });
      };

    const difference = (
        parseFloat((upcomingInvoiceData?.subtotal / 100).toFixed(2)) - 
        parseFloat((upcomingInvoiceData?.total / 100).toFixed(2))
      ).toFixed(2);

    return (
        <div className="plan-detail [.plan-detail+&]:mt-11">
            <h5 className="text-font-14 font-semibold text-b2 mb-5 border-b border-b11 pb-1.5">
                UPCOMING INVOICE
            </h5>
            {upcomingLoading && <ThreeDotLoader />}
            {!upcomingLoading && upcomingInvoiceData && (
                <div>
                <p className='text-font-14'><strong>Invoice Date:</strong> {formatDate(upcomingInvoiceData.period_end)}</p>
          
                <table style={tableStyles as any} className='text-font-14'>
                  <thead>
                    <tr>
                      <th style={thStyles}>Description</th>
                      <th style={thStyles}>Billing Period</th>
                      <th style={thStyles}>Members</th>
                      <th style={thStyles}>Unit Price</th>
                      <th style={thStyles}>Amount</th>
                    </tr>
                  </thead>
                  <tbody>
                    {upcomingInvoiceData.lines.data.map((line, index) => (
                      <tr key={index}>
                        <td style={tdStyles}>{line.description}</td>
                        <td style={tdStyles}>
                          {line.period
                            ? `${formatDate(line.period.start)} - ${formatDate(line.period.end)}`
                            : 'N/A'}
                        </td>
                        <td style={tdStyles}>{line.quantity}</td>
                        <td style={tdStyles}>
                          {line.plan && line.plan.amount
                            ? `${showCurrencySymbol(line.plan.currency)}${(line.plan.amount / 100).toFixed(2)} per ${line.plan.interval_count} ${line.plan.interval}`
                            : 'N/A'}
                        </td>
                        <td style={tdStyles}>{showCurrencySymbol(line.plan.currency)}{(line.amount / 100).toFixed(2)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
          
                <div style={summaryContainerStyles as any}>
                  <p><strong>Subtotal:</strong> {showCurrencySymbol(upcomingInvoiceData?.currency)}{(upcomingInvoiceData.subtotal / 100).toFixed(2)}</p>
                  {upcomingInvoiceData.discount && (
                    <p>
                      <strong>Discount:</strong> 
                      ({upcomingInvoiceData.discount.coupon.name}) (-{showCurrencySymbol(upcomingInvoiceData?.currency)}{difference})                      
                    </p>
                  )}
                  <p><strong>Total Excluding Tax:</strong> {showCurrencySymbol(upcomingInvoiceData?.currency)}{(upcomingInvoiceData.total_excluding_tax / 100).toFixed(2)}</p>
                  <p><strong>Total:</strong> {showCurrencySymbol(upcomingInvoiceData?.currency)}{(upcomingInvoiceData.total / 100).toFixed(2)}</p>
                  <p><strong>Amount Due:</strong> {showCurrencySymbol(upcomingInvoiceData?.currency)}{(upcomingInvoiceData.amount_due / 100).toFixed(2)}</p>
                </div>
              </div>
            )}
        </div>
    );
};

export default UpcomingInvoice; 