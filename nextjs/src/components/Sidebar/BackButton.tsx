'use client';
import Link from 'next/link';
import ArrowBack from '@/icons/ArrowBack';
import routes from '@/utils/routes';
import { useSidebar } from '@/context/SidebarContext';

const BackButton = () => {
  const { closeSidebar } = useSidebar();

  return (
    <Link
      className="w-8 h-8 ml-6 flex items-center justify-center rounded-md bg-b12 p-2 hover:bg-b11 cursor-pointer"
      href={routes.main}
      onClick={closeSidebar}
    >
      <ArrowBack width={18} height={18} className="fill-b2 w-[18px] h-auto" />
    </Link>
  );
};

export default BackButton;