'use client';

import { useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import {
    Tooltip,
    TooltipContent,
    TooltipProvider,
    TooltipTrigger,
} from '@/components/ui/tooltip';
import TrialCard from './FreeTrialCard';

const CircularProgress=({
    value,
    max,
    width,
}: {
    value: number;
    max: number;
    width: number;
}) => {
    const [showTooltip, setShowTooltip] = useState(false);

    const radius = (width - 4) / 2;
    const circumference = 2 * Math.PI * radius;
    const dash = ((value / max) * 100 * circumference) / 100;

    return (
        <Card className="hidden md:block w-full max-w-xs bg-white">
            <CardContent className="flex justify-center">
                <TooltipProvider>
                    <Tooltip open={showTooltip} onOpenChange={setShowTooltip}>
                        <TooltipTrigger asChild>
                            <button
                                className="relative flex items-center justify-center outline-none"
                                onClick={() => setShowTooltip(!showTooltip)}
                            >
                                <svg
                                    width={width}
                                    height={width}
                                    viewBox={`0 0 ${width} ${width}`}
                                >
                                    <circle
                                        cx={width / 2}
                                        cy={width / 2}
                                        r={radius}
                                        fill="none"
                                        stroke="#f0f0f0"
                                        strokeWidth={4}
                                    />
                                    <circle
                                        cx={width / 2}
                                        cy={width / 2}
                                        r={radius}
                                        fill="none"
                                        stroke={value < 5 ? "red" : "#8D3CE2"}
                                        strokeWidth={4}
                                        strokeDasharray={`${dash} ${
                                            circumference - dash
                                        }`}
                                        strokeLinecap="round"
                                        transform={`rotate(-90 ${width / 2} ${
                                            width / 2
                                        })`}
                                    />
                                </svg>
                                <div className="absolute inset-0 flex items-center justify-center">
                                    <span className={`text-2xl font-medium ${value < 5 ? "text-red-500" : "text-purple-500"}`}>
                                        {value}
                                    </span>
                                </div>
                            </button>
                        </TooltipTrigger>
                        <TooltipContent
                            side="top"
                            className="bg-white text-white border mr-10"
                        >
                           <TrialCard daysLeft={value} totalDays={max} />
                        </TooltipContent>
                    </Tooltip>
                </TooltipProvider>
            </CardContent>
        </Card>
    );
}

export default CircularProgress;