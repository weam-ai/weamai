import React from 'react';
import { Doughnut } from 'react-chartjs-2';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';

ChartJS.register(ArcElement, Tooltip, Legend);

const DoughnutChartBilling = ({ value, maxValue, size = 'md' }) => {
  const sizeConfig = {
    sm: {
      containerClass: 'w-[70px] h-[70px]',
      cutout: '82%',
      textClass: 'text-font-10 mt-[7px]',
      subTextClass: 'text-[8px]'
    },
    md: {
      containerClass: 'w-[90px] h-[90px]',
      cutout: '82%',
      textClass: 'text-font-12 mt-[9px]',
      subTextClass: 'text-[10px]'
    }
  };

  const config = sizeConfig[size] || sizeConfig.md;

  const data = {
    datasets: [
      {
        data: [value, maxValue - value],
        backgroundColor: ['#A6A6A6', '#E6E6E6'],
        hoverBackgroundColor: ['#A6A6A6', '#E6E6E6'],
      },
    ],
  };

  const options = {
    cutout: config.cutout,
    rotation: -90,
    circumference: 180,
    maintainAspectRatio: true,
    responsive: true,
    plugins: {
      tooltip: { enabled: false },
    },
  };

  return (
    <div className={`relative ${config.containerClass}`}>
      <Doughnut data={data} options={options} />
      <div className='absolute top-1/2 left-1/2 -translate-y-1/2 -translate-x-1/2 text-center'>
        <div className={`font-semibold text-b2 ${config.textClass}`}>{value}mb</div>
        <div className={`font-semibold text-b6 ${config.subTextClass}`}>of {maxValue}mb</div>
      </div>
    </div>
  );
};

export default DoughnutChartBilling;