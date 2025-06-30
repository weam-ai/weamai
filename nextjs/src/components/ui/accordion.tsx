"use client"

import * as React from "react"
import * as AccordionPrimitive from "@radix-ui/react-accordion"
import ArrowIcon from '../../icons/ArrowIcon';

import { cn } from "@/lib/utils"

const Accordion = AccordionPrimitive.Root

const AccordionItem = React.forwardRef(({ className, ...props }:any, ref) => (
  <AccordionPrimitive.Item ref={ref} className={cn("border-b", className)} {...props}  />
))
AccordionItem.displayName = "AccordionItem"

const AccordionTrigger = React.forwardRef(({ className, children, subtitle, ...props }, ref) => (
  <AccordionPrimitive.Header className="flex">
    <AccordionPrimitive.Trigger
      ref={ref}
      className={cn(
        "flex flex-1 items-center justify-between transition-all [&[data-state=open]>span>.accordion-icon]:rotate-0 [&[data-state=open]>.triangle-icon]:rotate-90",
        className
      )}
      {...props}>
      {children}
      <span className='ms-auto shrink-0 flex'>
        {subtitle && <span className="accordion-subtitle text-font-16 leading-none font-semibold text-b6 inline-block me-2.5">{subtitle}</span>}
        <span className="accordion-icon shrink-0 h-5 w-5 -rotate-90 transition-transform duration-200 ease-in-out motion-reduce:transition-none [&>svg]:h-5 [&>svg]:w-5 [&>svg]:object-contain [&>svg]:stroke-white">
            <ArrowIcon />
        </span>
      </span>
    </AccordionPrimitive.Trigger>
  </AccordionPrimitive.Header>
))
AccordionTrigger.displayName = AccordionPrimitive.Trigger.displayName

const AccordionContent = React.forwardRef(({ className, children, ...props }, ref) => (
  <AccordionPrimitive.Content
    ref={ref}
    className="overflow-hidden text-sm transition-all data-[state=closed]:animate-accordion-up data-[state=open]:animate-accordion-down"
    {...props}>
    <div className={cn(className)}>{children}</div>
  </AccordionPrimitive.Content>
))

AccordionContent.displayName = AccordionPrimitive.Content.displayName

export { Accordion, AccordionItem, AccordionTrigger, AccordionContent }
