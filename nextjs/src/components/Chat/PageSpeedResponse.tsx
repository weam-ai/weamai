import React from 'react'
import DesktopIcon from '@/icons/DesktopIcon';
import ErrorAuditIcon from '@/icons/ErrorAuditIcon';
import MobileIcon from '@/icons/MobileIcon';
import PassAuditIcon from '@/icons/PassAuditIcon';
import WarningAuditIcon from '@/icons/WarningAuditIcon';
import { MarkOutPut } from './MartOutput';

type MetricValue = {
    value: number;
    unit?: 'SECONDS' | 'MILLISECONDS' | 'N/A' | string;
    tag: string;
};

type DiagnoseCategory = {
    score: number;
    tag: string;
};

type DiagnosePerformance = {
    Performance: DiagnoseCategory;
    Accessibility: DiagnoseCategory;
    'Best Practices': DiagnoseCategory;
    SEO: DiagnoseCategory;
    'Total Blocking Time': MetricValue;
    'Speed Index': MetricValue;
};

type Metrics = {
    'Largest Contentful Paint (LCP)': MetricValue;
    'Interaction to Next Paint (INP)': number;
    'Cumulative Layout Shift (CLS)': MetricValue;
    'First Contentful Paint (FCP)': MetricValue;
    'Time to First Byte (TTFB)': number;
};

type DeviceMetrics = {
    'Core Web Vitals Assessment': string;
    Metrics: Metrics;
    'Diagnose Performance Issues': DiagnosePerformance;
};

type PageSpeedResponseProps = {
    response: {
        desktop_metrics: DeviceMetrics;
        mobile_metrics: DeviceMetrics;
        file_url: string;
    };
};

const getTagIcon = (tag: string) => {
    switch (tag) {
        case 'Warning':
        case 'Orange (moderate)':
            return <WarningAuditIcon width={12} height={12} className="fill-orange w-3 h-auto" />;
        case 'Fail':
        case 'Red (slow)':
            return <ErrorAuditIcon width={14} height={14} className="fill-red w-3.5 h-auto" />;
        case 'Pass': 
        case 'Good':
            return <PassAuditIcon width={12} height={12} className="fill-green w-3 h-auto" />;
        default:
            return null;
    }
}; 

const getFormattedUnit = (unit: string) => {
    const unitObj = {
        SECONDS: 's',
        MILLISECONDS: 'ms',
    };
    return unitObj[unit as keyof typeof unitObj] || '';
};
const PageSpeedResponse = ({ response }: PageSpeedResponseProps) => {
    const renderMetricValue = (value: number | MetricValue) => {
        if (typeof value === 'number') return <span>{value}</span>;
        return (
            <span className="flex items-center gap-1">
                <span>
                    {getTagIcon(value.tag)}
                </span>
                <span>{value.value}</span>
                <span>{getFormattedUnit(value.unit)}</span>
            </span>
        );
    };
    

    const renderDiagnoseCategory = (category: DiagnoseCategory | MetricValue) => {
        const scoreOrValue = 'score' in category ? category.score : category.value;
        return (
            <div className="flex items-center">
                <span className="text-xs text-gray-500 flex items-center gap-1 mr-1">
                     {getTagIcon(category.tag)}
                </span>
                <span className='text-font-18 font-semibold'>{scoreOrValue}</span>
            </div>
        );
    };
    
    const getDeviceIcon = (deviceKey: string) => {
        switch (deviceKey) {
            case 'desktop_metrics':
                return <DesktopIcon width={16} height={16} className="inline-block w-4 h-auto mr-1 fill-black" />;
            case 'mobile_metrics':
                return <MobileIcon width={12} height={12} className="inline-block w-3 h-auto mr-1" />;
            default:
                return null;
        }
    };

    const getDeviceLabel = (deviceKey: string) => {
        switch (deviceKey) {
            case 'desktop_metrics':
                return 'Desktop Metrics';
            case 'mobile_metrics':
                return 'Mobile Metrics';
            default:
                return deviceKey.replace('_', ' ');
        }
    };

    return (
        <div className="flex flex-col gap-6 my-2">
            {(['desktop_metrics', 'mobile_metrics'] as const).map((deviceKey) => {
                const deviceMetrics = response[deviceKey];
                return (
                    <div key={deviceKey} className="border p-4 rounded text-font-14">
                        <h2 className="font-bold capitalize flex items-center gap-1 mb-2 pb-2 border-b">
                            {getDeviceIcon(deviceKey)} {getDeviceLabel(deviceKey)}
                        </h2>                        
                        <p className="mb-4 text-center">
                            Core Web Vitals Assessment: <strong className='text-red'>{deviceMetrics['Core Web Vitals Assessment']}</strong>
                        </p>

                    <div className="mb-4">
                        <div className="space-y-1">
                            {deviceMetrics?.Metrics && Object.entries(deviceMetrics.Metrics).map(([metricKey, metricValue]) => (
                                <div key={metricKey} className="flex justify-between border-b py-1.5 max-md:flex-col">
                                    <span>{metricKey}</span>
                                    <span>{renderMetricValue(metricValue)}</span>
                                </div>
                            ))}
                        </div>
                    </div>

                    <div>
                        <h3 className="mb-3 text-center">Diagnose Performance Issues</h3>
                        <div className="flex justify-center gap-2 flex-wrap max-md:flex-col">
                            {deviceMetrics?.['Diagnose Performance Issues'] && Object.entries(deviceMetrics['Diagnose Performance Issues']).map(([key, value]) => (
                                <div key={key} className="flex flex-col justify-center items-center w-1/4 max-md:w-full p-2 rounded-md border">
                                    {renderDiagnoseCategory(value)}
                                    <span>{key}</span>
                                </div>
                            ))}
                        </div>
                        </div>
                    </div>
                );
            })}
            {response?.file_url && MarkOutPut(response.file_url)}
        </div>
    );
};

export default PageSpeedResponse;
