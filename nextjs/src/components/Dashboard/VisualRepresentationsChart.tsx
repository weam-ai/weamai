'use client';
import React, { useState } from 'react';
import { Doughnut } from 'react-chartjs-2';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';
import Select from 'react-select';

ChartJS.register(ArcElement, Tooltip, Legend);

const VisualRepresentationsOptions = [
    { value: 'yearly', label: 'Yearly' },
    { value: 'monthly', label: 'Monthly' },
    { value: 'weekly', label: 'Weekly' },
];

const dataSets = {
    yearly: {
        labels: ['Active Companies', 'Active Users', 'Workspaces'],
        datasets: [
            {
                data: [30, 50, 20],
                backgroundColor: ['#8D3CE2', '#FF6D0A', '#40BD7E'],
                borderColor: ['#8D3CE2', '#FF6D0A', '#40BD7E'],
                borderWidth: 1,
            },
        ],
    },
    monthly: {
        labels: ['Active Companies', 'Active Users', 'Workspaces'],
        datasets: [
            {
                data: [25, 60, 15],
                backgroundColor: ['#8D3CE2', '#FF6D0A', '#40BD7E'],
                borderColor: ['#8D3CE2', '#FF6D0A', '#40BD7E'],
                borderWidth: 1,
            },
        ],
    },
    weekly: {
        labels: ['Active Companies', 'Active Users', 'Workspaces'],
        datasets: [
            {
                data: [20, 70, 10],
                backgroundColor: ['#8D3CE2', '#FF6D0A', '#40BD7E'],
                borderColor: ['#8D3CE2', '#FF6D0A', '#40BD7E'],
                borderWidth: 1,
            },
        ],
    },
};

const options = {
    cutout: '70%',
    responsive: true,
    plugins: {
        legend: {
            display: false, // Disable the built-in legend
        },
        tooltip: {
            callbacks: {
                label: function (context) {
                    let label = context.label || '';
                    if (label) {
                        label += ': ';
                    }
                    label += Math.round(context.raw) + '%';
                    return label;
                },
            },
        },
    },
};

const VisualRepresentationsChart = () => {
    const [selectedOption, setSelectedOption] = useState(VisualRepresentationsOptions[0]);

    const handleSelectChange = (selectedOption) => {
        setSelectedOption(selectedOption);
    };

    return (
        <div className="bg-purple/10 rounded-10 p-5 flex flex-col h-full">
            <div className="flex items-start justify-between mb-8">
                <div className="me-3">
                    <h5 className="text-font-18 font-semibold text-b2 mb-2">
                        Visual Representations of Activity
                    </h5>
                </div>
                <Select
                    options={VisualRepresentationsOptions}
                    menuPlacement="auto"
                    className="react-select-container b-white w-[130px]"
                    classNamePrefix="react-select"
                    defaultValue={VisualRepresentationsOptions[0]}
                    onChange={handleSelectChange}
                />
            </div>
            <div className="visual-representations-activity flex-1">
                <div className="h-[280px] mx-auto flex itm justify-center mb-9">
                    <Doughnut
                        data={dataSets[selectedOption.value]}
                        options={options}
                    />
                </div>
                <div className="flex items-center justify-between gap-2 mt-auto w-full">
                    {dataSets[selectedOption.value].labels.map((label, index) => (
                        <div key={index} className="flex items-center">
                            <div
                                className="size-3 rounded-full me-2.5"
                                style={{
                                    backgroundColor:
                                        dataSets[selectedOption.value].datasets[0]
                                            .backgroundColor[index],
                                }}
                            ></div>
                            <span className="text-font-14 text-b5">
                                {label}
                            </span>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default VisualRepresentationsChart;