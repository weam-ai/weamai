import React, { useState, useEffect } from 'react';
import { Bar } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend } from 'chart.js';
import Select from 'react-select';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

const UserOptions = [
  { value: 'yearly', label: 'Yearly' },
  { value: 'monthly', label: 'Monthly' },
  { value: 'weekly', label: 'Weekly' },
];

const userData = {
  yearly: [1000, 2300, 2542, 6854, 6584, 4562, 2222, 4756, 1256, 6326, 1878, 6256],
  monthly: [2652, 4532, 2561, 8525, 6258, 4256, 2222, 7125, 1226, 3252, 8157, 2235],
  weekly: [2542, 6854, 6584, 4562, 1226, 3252, 8157, 2235, 8525, 6258, 4256, 2222],
};

const generateChartData = (userOption) => {
  return {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
    datasets: [
      {
        label: userOption,
        data: userData[userOption],
        backgroundColor: '#40BD7E',
        borderColor: '#40BD7E',
        borderWidth: 1,
        borderRadius: { topLeft: 10, topRight: 10 },
        barThickness: 10,
        maxBarThickness: 10,
        barPercentage: 0.5,
      },
    ],
  };
};

const UserSubscribedReport = () => {
  const [selectedUser, setSelectedUserOptions] = useState(UserOptions[0].value);
  const [chartData, setChartData] = useState(generateChartData(UserOptions[0].value));
  const [totalUser, setTotalUser] = useState(userData[UserOptions[0].value].reduce((acc, value) => acc + value, 0));

  useEffect(() => {
    const data = generateChartData(selectedUser);
    setChartData(data);
    const total = userData[selectedUser].reduce((acc, value) => acc + value, 0);
    setTotalUser(total);
  }, [selectedUser]);

  const handleUserOptionsChange = (selectedOption) => {
    setSelectedUserOptions(selectedOption.value);
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
    },
    scales: {
      x: {
        borderColor: '#D9D9D9',
        grid: {
          display: false,
        },
      },
      y: {
        beginAtZero: true,
        borderWidth: 0,
        grid: {
          display: true,
          borderWidth: 1,
          borderColor: '#D9D9D9',
        },
      },
    },
  };

  return (
    <div className='border border-b11 rounded-10 p-5 flex flex-col h-full w-full'>
      <div className='flex items-start justify-between mb-8'>
        <div className='me-3'>
          <h5 className='text-font-18 font-semibold text-b2 mb-2'>User Subscribed Report</h5>
          <h4 className='text-font-24 font-semibold text-green'>{totalUser} users</h4>
        </div>
        <Select
          options={UserOptions}
          menuPlacement="auto"
          className="react-select-container b-white min-w-[130px]"
          classNamePrefix="react-select"
          defaultValue={UserOptions[0]}
          onChange={handleUserOptionsChange}
        />
      </div>
      <div className='h-[310px]'>
        <Bar data={chartData} options={options} />
      </div>
    </div>
  );
};

export default UserSubscribedReport;
