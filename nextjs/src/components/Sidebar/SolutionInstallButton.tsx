"use client";
import commonApi from '@/api';
import { MODULE_ACTIONS } from '@/utils/constant';
import { useState } from 'react';

const SolutionInstallButton = () => {
    const [loading, setLoading] = useState(false);

    const handleInstall = async () => {
        try {
            setLoading(true);
            const response = await commonApi({
                action: MODULE_ACTIONS.SOLUTION_INSTALL,
                data: { source: 'sidebar' }
            });
            // Optional: show toast if available
            // Toast(response?.message || 'Triggered installation');
            console.log('solution-install response:', response);
        } catch (error) {
            console.error('solution-install error:', error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <button
            onClick={handleInstall}
            disabled={loading}
            className="w-full mb-3 text-left px-2 py-2 rounded hover:bg-b5 hover:bg-opacity-[0.12] text-font-14"
        >
            {loading ? 'Installing…' : 'Install Solution'}
        </button>
    );
};

export default SolutionInstallButton;


