import { FormatCompanyType, ModalConfigType, FormatBotType, ObjectType } from '@/types/common';

export type SubModelType = {
    id:string;
    _id: string;
    bot: FormatBotType;
    company: FormatCompanyType;
    modelType: number;
    name: string;
    config: ModalConfigType;
    isDisable: boolean;
    provider?: string;
  };

export type AiModalType = {
    _id:       string;
    name:      string;
    modelType: number;
    isActive:  boolean;
    createdAt: Date;
    updatedAt: Date;
    bot:       FormatBotType;
    company:   FormatCompanyType;
    config:    ModalConfigType;
    extraConfig:  ObjectType;
    provider?:  string;
    isDisable?: boolean;
}
