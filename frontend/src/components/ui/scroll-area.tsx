import * as React from "react"
import * as anyPrimitive from "@radix-ui/react-scroll-area"
import { cn } from "@/lib/utils"

const ScrollArea = React.forwardRef<
    React.ElementRef<typeof anyPrimitive.Root>,
    React.ComponentPropsWithoutRef<typeof anyPrimitive.Root>
>(({ className, children, ...props }, ref) => (
    <anyPrimitive.Root
        ref={ref}
        className={cn("relative overflow-hidden", className)}
        {...props}
    >
        <anyPrimitive.Viewport className="h-full w-full rounded-[inherit]">
            {children}
        </anyPrimitive.Viewport>
        <ScrollBar />
        <anyPrimitive.Corner />
    </anyPrimitive.Root>
))
ScrollArea.displayName = anyPrimitive.Root.displayName

const ScrollBar = React.forwardRef<
    React.ElementRef<typeof anyPrimitive.ScrollAreaScrollbar>,
    React.ComponentPropsWithoutRef<typeof anyPrimitive.ScrollAreaScrollbar>
>(({ className, orientation = "vertical", ...props }, ref) => (
    <anyPrimitive.ScrollAreaScrollbar
        ref={ref}
        orientation={orientation}
        className={cn(
            "flex touch-none select-none transition-colors",
            orientation === "vertical" &&
            "h-full w-2.5 border-l border-l-transparent p-[1px]",
            orientation === "horizontal" &&
            "h-2.5 flex-col border-t border-t-transparent p-[1px]",
            className
        )}
        {...props}
    >
        <anyPrimitive.ScrollAreaThumb className="relative flex-1 rounded-full bg-border" />
    </anyPrimitive.ScrollAreaScrollbar>
))
ScrollBar.displayName = anyPrimitive.ScrollAreaScrollbar.displayName

export { ScrollArea, ScrollBar }
