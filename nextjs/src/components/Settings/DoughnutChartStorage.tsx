'use client';

import React from 'react';
import { Doughnut } from 'react-chartjs-2';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';

ChartJS.register(ArcElement, Tooltip, Legend);

const DoughnutChartStorage = ({ used, total }) => {
  const available = total - used;

  const data = {
    datasets: [
      {
        data: [used, available],
        backgroundColor: ['#5065F6', '#D9D9D9'],
        hoverBackgroundColor: ['#5065F6', '#D9D9D9'],
      },
    ],
  };

  const options = {
    cutout: '80%',
    rotation: -90,
    circumference: 180,
    plugins: {
      tooltip: { enabled: false },
    },
  };

  return (
    <div className='w-[210px]'>
        <div className='flex items-center justify-center overflow-hidden h-[75px]'>
            <div className='relative w-[150px] h-[150px] mx-auto'>
                <Doughnut data={data} options={options} />
                <div className='absolute top-1/2 left-1/2 -translate-y-1/2 -translate-x-1/2 text-center mt-4'>
                    <div className='text-b6 text-font-14 leading-none font-normal'><span className='text-font-18 leading-none text-b2 font-semibold'>{used}</span> mb</div>
                    <div className='text-font-14 font-normal text-b6'>Used</div>
                </div>
            </div>
        </div>
        <div className='flex justify-between mt-2.5'>
            <div className='text-center'>
                <div className='text-font-12 font-normal text-b6'>Total Space</div>
                <div className='text-b6 text-font-14 leading-none font-normal'><span className='text-font-14 leading-none text-b2 font-semibold'>{total}</span> mb</div>
            </div>
            <div className='text-center'>
                <div className='text-font-12 font-normal text-b6'>Available Space</div>
                <div className='text-b6 text-font-14 leading-none font-normal'><span className='text-font-14 leading-none text-b2 font-semibold'>{available}</span> mb</div>
            </div>
        </div>
    </div>
  );
};

export default DoughnutChartStorage;