import { addConfigEnvAction } from '@/actions/storage';
import useServerAction from '@/hooks/common/useServerActions';
import { RESPONSE_STATUS } from '@/utils/constant';
import Toast from '@/utils/toast';
import Label from '@/widgets/Label';
import React, { useState, useCallback, useMemo } from 'react';

// Types
type FormData = {
    // email fields
    // SMTP fields
    SMTP_USERNAME: string;
    SMTP_PASSWORD: string;
    SMTP_HOST: string;
    SMTP_PORT: string;
    // SES fields
    AWS_SES_ACCESS_KEY_ID: string;
    AWS_SES_SECRET_ACCESS_KEY: string;
    AWS_SES_REGION: string;
    AWS_SES_VERIFIED_MAIL: string;
    
    // storage fields
    // S3 fields
    AWS_S3_ACCESS_KEY: string;
    AWS_S3_BUCKET_NAME: string;
    AWS_SESSION_TOKEN: string;
    AWS_S3_SECRET_KEY: string;
    AWS_S3_URL: string;
    AWS_S3_API_VERSION: string;
    AWS_ACCESS_ID: string;
    AWS_SECRET_KEY: string;
    AWS_REGION: string;
    // localstack fields
    LSTACK_ACCESS_KEY_ID: string;
    LSTACK_REGION: string;
    LSTACK_SECRET_ACCESS_KEY: string;
    LSTACK_CDN_URL: string;
    REGEX_FILE_PATTERN: string;
    LSTACK_BUCKET: string;
    SERVICES: string;
    DATA_DIR: string;
    DOCKER_HOST: string;
    LSTACK_PORT: string;
    USE_SSL: string;
    DEBUG: string;
    LSTACK_VECTORS_BACKUP: string;


    // Firebase fields
    FIREBASE_APP_ID: string;
    FIREBASE_VAPID_KEY: string;
    FIREBASE_API_KEY: string;
    FIREBASE_AUTH_DOMAIN: string;
    FIREBASE_PROJECT_ID: string;
    FIREBASE_STORAGE_BUCKET: string;
    FIREBASE_MESSAGING_SENDER_ID: string;
    FIREBASE_MEASUREMENT_ID: string;
}

type FormSection = {
    title: string;
    code: string;
    fields: Array<{
        key: keyof FormData;
        label: string;
        type: 'text' | 'password';
        placeholder?: string;
        required: boolean;
    }>;
}

// Configuration constants
const FORM_SECTIONS: FormSection[] = [
    {
        title: 'Email',
        code: 'EMAIL',
        fields: [
            { key: 'SMTP_USERNAME', label: 'SMTP Username', type: 'text', required: true },
            { key: 'SMTP_PASSWORD', label: 'SMTP Password', type: 'password', required: true },
            { key: 'SMTP_HOST', label: 'SMTP Host', type: 'text', required: true },
            { key: 'SMTP_PORT', label: 'SMTP Port', type: 'text', required: true },

            //or
            { key: 'AWS_SES_ACCESS_KEY_ID', label: 'SES Access Key', type: 'text', required: true },
            { key: 'AWS_SES_SECRET_ACCESS_KEY', label: 'SES Secret Key', type: 'password', required: true },
            { key: 'AWS_SES_REGION', label: 'SES Region', type: 'text', required: true },
            { key: 'AWS_SES_VERIFIED_MAIL', label: 'SES From Address', type: 'text', required: true },
        ]
    },
    {
        title: 'Storage',
        code: 'STORAGE',
        fields: [
            //s3 fields
            { key: 'AWS_S3_ACCESS_KEY', label: 'AWS S3 Access Key', type: 'text', placeholder: 'AWS_S3_ACCESS_KEY', required: true },
            { key: 'AWS_S3_BUCKET_NAME', label: 'AWS S3 Bucket Name', type: 'text', placeholder: 'AWS_S3_BUCKET_NAME', required: true },
            { key: 'AWS_SESSION_TOKEN', label: 'AWS Session Token', type: 'text', placeholder: 'AWS_SESSION_TOKEN', required: true },
            { key: 'AWS_S3_SECRET_KEY', label: 'AWS S3 Secret Key', type: 'password', placeholder: 'AWS_S3_SECRET_KEY', required: true },
            { key: 'AWS_S3_URL', label: 'AWS S3 URL', type: 'text', placeholder: 'AWS_S3_URL', required: true },
            { key: 'AWS_S3_API_VERSION', label: 'AWS S3 API Version', type: 'text', placeholder: 'AWS_S3_API_VERSION', required: true },
            { key: 'AWS_ACCESS_ID', label: 'AWS Access ID', type: 'text', placeholder: 'AWS_ACCESS_ID', required: true },
            { key: 'AWS_SECRET_KEY', label: 'AWS Secret Key', type: 'password', placeholder: 'AWS_SECRET_KEY', required: true },
            { key: 'AWS_REGION', label: 'AWS Region', type: 'text', placeholder: 'REGION', required: true },

            //or
            { key: 'LSTACK_ACCESS_KEY_ID', label: 'LSTACK Access Key', type: 'text', placeholder: 'LSTACK_ACCESS_KEY_ID', required: true },
            { key: 'LSTACK_REGION', label: 'LSTACK Region', type: 'text', placeholder: 'LSTACK_REGION', required: true },
            { key: 'LSTACK_SECRET_ACCESS_KEY', label: 'LSTACK Secret Access Key', type: 'password', placeholder: 'LSTACK_SECRET_ACCESS_KEY', required: true },
            { key: 'LSTACK_CDN_URL', label: 'LSTACK CDN URL', type: 'text', placeholder: 'LSTACK_CDN_URL', required: true },
            { key: 'REGEX_FILE_PATTERN', label: 'REGEX File Pattern', type: 'text', placeholder: 'REGEX_FILE_PATTERN', required: true },
            { key: 'LSTACK_BUCKET', label: 'LSTACK Bucket', type: 'text', placeholder: 'LSTACK_BUCKET', required: true },
            { key: 'SERVICES', label: 'SERVICES', type: 'text', placeholder: 'SERVICES', required: true },
            { key: 'DATA_DIR', label: 'DATA DIR', type: 'text', placeholder: 'DATA_DIR', required: true },
            { key: 'DOCKER_HOST', label: 'DOCKER HOST', type: 'text', placeholder: 'DOCKER_HOST', required: true },
            { key: 'LSTACK_PORT', label: 'LSTACK PORT', type: 'text', placeholder: 'LSTACK_PORT', required: true },
            { key: 'USE_SSL', label: 'USE SSL', type: 'text', placeholder: 'USE_SSL', required: true },
            { key: 'DEBUG', label: 'DEBUG', type: 'text', placeholder: 'DEBUG', required: true },
            { key: 'LSTACK_VECTORS_BACKUP', label: 'LSTACK Vectors Backup', type: 'text', placeholder: 'LSTACK_VECTORS_BACKUP', required: true },
        ]
    },
    {
        title: 'Firebase',
        code: 'FIREBASE_PRIVATE_KEY',
        fields: [
            { key: 'FIREBASE_APP_ID', label: 'Firebase App ID', type: 'text', placeholder: 'NEXT_PUBLIC_FIREBASE_APP_ID', required: true },
            { key: 'FIREBASE_VAPID_KEY', label: 'Firebase VAPID Key', type: 'text', placeholder: 'NEXT_PUBLIC_FIREBASE_VAPID_KEY', required: true },
            { key: 'FIREBASE_API_KEY', label: 'Firebase API Key', type: 'text', placeholder: 'NEXT_PUBLIC_FIREBASE_API_KEY', required: true },
            { key: 'FIREBASE_AUTH_DOMAIN', label: 'Firebase Auth Domain', type: 'text', placeholder: 'NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN', required: true },
            { key: 'FIREBASE_PROJECT_ID', label: 'Firebase Project ID', type: 'text', placeholder: 'NEXT_PUBLIC_FIREBASE_PROJECT_ID', required: true },
            { key: 'FIREBASE_STORAGE_BUCKET', label: 'Firebase Storage Bucket', type: 'text', placeholder: 'NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET', required: true },
            { key: 'FIREBASE_MESSAGING_SENDER_ID', label: 'Firebase Messaging Sender ID', type: 'text', placeholder: 'NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID', required: true },
            { key: 'FIREBASE_MEASUREMENT_ID', label: 'Firebase Measurement ID', type: 'text', placeholder: 'NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID', required: true }
        ]
    }
];

const FormField: React.FC<{
    field: FormSection['fields'][0];
    value: string;
    error?: string;
    onChange: (key: keyof FormData, value: string) => void;
}> = ({ field, value, error, onChange }) => (
    <div className="flex items-center gap-2.5">
        <Label
            title={field.label}
            htmlFor={field.key}
            required={field.required}
            className="w-full"
        />
        <input
            type={field.type}
            className={`default-form-input w-10 ${error ? 'border-red-500' : ''}`}
            id={field.key}
            placeholder={field.placeholder}
            value={value}
            onChange={(e) => onChange(field.key, e.target.value)}
        />
    </div>
);

const FormSection: React.FC<{
    section: FormSection;
    formData: FormData;
    errors: Record<string, string>;
    onInputChange: (key: keyof FormData, value: string) => void;
    onSave: (sectionFields: (keyof FormData)[], name: string, code: string) => void;
    isPending: boolean;
}> = ({ section, formData, errors, onInputChange, onSave, isPending }) => {
    const sectionFields = section.fields.map(field => field.key);
    
    const handleSave = useCallback((e: React.FormEvent) => {
        e.preventDefault();
        onSave(sectionFields, section.title, section.code);
    }, [onSave, sectionFields, section.title, section.code]);

    return (
        <div className="relative mb-4">
            <Label
                title={section.title}
                htmlFor={section.title.toLowerCase()}
                required={false}
                className="text-font-20 font-semibold block mb-2 text-b2"
            />
            
            {section.fields.map((field) => (
                <div key={field.key}>
                    <FormField
                        field={field}
                        value={formData[field.key]}
                        error={errors[field.key]}
                        onChange={onInputChange}
                    />
                    {errors[field.key] && (
                        <p className="text-red text-sm mt-1">{errors[field.key]}</p>
                    )}
                </div>
            ))}

            <div className="flex items-center gap-2.5 mt-4">
                <button 
                    type="button"
                    className="btn btn-blue"
                    onClick={handleSave}
                    disabled={isPending}
                >
                    {isPending ? 'Saving...' : 'Save Changes'}
                </button>
            </div>
        </div>
    );
};

const Environment = () => {
    const [formData, setFormData] = useState<FormData>({
        // SMTP fields
        SMTP_USERNAME: '',
        SMTP_PASSWORD: '',
        SMTP_HOST: '',
        SMTP_PORT: '',
        
        // S3 fields
        AWS_S3_ACCESS_KEY: '',
        AWS_S3_BUCKET_NAME: '',
        AWS_SESSION_TOKEN: '',
        AWS_S3_SECRET_KEY: '',
        AWS_S3_URL: '',
        AWS_S3_API_VERSION: '',
        AWS_ACCESS_ID: '',
        AWS_SECRET_KEY: '',
        AWS_REGION: '',
        
        // Firebase fields
        FIREBASE_APP_ID: '',
        FIREBASE_VAPID_KEY: '',
        FIREBASE_API_KEY: '',
        FIREBASE_AUTH_DOMAIN: '',
        FIREBASE_PROJECT_ID: '',
        FIREBASE_STORAGE_BUCKET: '',
        FIREBASE_MESSAGING_SENDER_ID: '',
        FIREBASE_MEASUREMENT_ID: ''
    });

    const [errors, setErrors] = useState<Record<string, string>>({});
    const [addConfigEnv, isPending] = useServerAction(addConfigEnvAction);

    // Memoized validation function
    const validateSection = useCallback((sectionFields: (keyof FormData)[]) => {
        const newErrors: Record<string, string> = {};
        let isValid = true;

        sectionFields.forEach(field => {
            if (!formData[field]?.trim()) {
                newErrors[field] = 'Above field is required';
                isValid = false;
            }
        });

        setErrors(prev => ({
            ...prev,
            ...newErrors
        }));

        return isValid;
    }, [formData]);

    const handleInputChange = useCallback((field: keyof FormData, value: string) => {
        setFormData(prev => ({
            ...prev,
            [field]: value
        }));
        
        if (errors[field]) {
            setErrors(prev => ({
                ...prev,
                [field]: ''
            }));
        }
    }, [errors]);

    const handleSave = useCallback(async (payload: Partial<FormData>, name: string, code: string) => {
        try {
            const reqPayload = {
                name,
                code,
                details: payload
               
            }
          
            const response = await addConfigEnv(reqPayload);
            console.log('Configuration saved:', response);
            if(response.status === RESPONSE_STATUS.SUCCESS){
                Toast(response.message);
            }
        } catch (error) {
            console.error('Failed to save configuration:', error);
        }
    }, [addConfigEnv]);

    const handleSectionSave = useCallback((sectionFields: (keyof FormData)[], name: string, code: string) => {
        if (validateSection(sectionFields)) {
            const sectionData = sectionFields.reduce((acc, field) => {
                acc[field] = formData[field];
                return acc;
            }, {} as Partial<FormData>);
            
            handleSave(sectionData, name, code);
        }
    }, [validateSection, formData, handleSave]);

    return (
        <form className="w-full mt-5">
            {FORM_SECTIONS.map((section) => (
                <FormSection
                    key={section.title}
                    section={section}
                    formData={formData}
                    errors={errors}
                    onInputChange={handleInputChange}
                    onSave={handleSectionSave}
                    isPending={isPending}
                />
            ))}
        </form>
    );
};

export default Environment;