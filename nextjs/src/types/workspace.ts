import { FormatCompanyType, ObjectType } from './common';

export type SelectedWorkSpaceType = {
    _id: string;
    title: string;
    slug: string;
    isActive?: boolean;
    isDefault?: boolean;
    createdBy?: string;
    createdAt?: string;
    updatedAt?: string;
    __v?: number;
};

export type WorkspaceListType = {
    company: FormatCompanyType;
    _id: string;
    title: string;
    slug: string;
    isActive: boolean;
    createdBy: string;
    isDefault: boolean;
    teams: ObjectType[];
    createdAt: string;
    updatedAt: string;
    __v: number;
    role: string;
};
