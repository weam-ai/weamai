import { FormatBrainType, FormatUserType, ObjectType } from './common';

export type PromptRecordType = {
    _id: string;
    title: string;
    brain: FormatBrainType;
    brandInfo?: null | ObjectType;
    companyInfo?: null | ObjectType;
    productInfo?: null | ObjectType;
    content: string;
    createdAt: string;
    defaultprompt: boolean;
    isActive: boolean;
    isCompleted: boolean;
    tags: string[];
    updatedAt: string;
    user: FormatUserType;
    website?: string[];
    isFavorite: boolean;
    favoriteByUsers: string[];
};
