"use client"

import * as React from "react"
import { X } from "lucide-react"
import { Badge } from "./ui/badge"
import { Command, CommandGroup, CommandItem } from "./ui/command"
import { Popover, PopoverContent, PopoverTrigger } from "./ui/popover"

type Option = {
  label: string
  value: string
}

type MultiSelectProps = {
  options: Option[]
  selected: Option[]
  onChange: (selected: Option[]) => void
  placeholder?: string
  className?: string
}

export function MultiSelect({
  options = [],
  selected = [],
  onChange,
  placeholder = "Select options...",
  className,
}: MultiSelectProps) {
  const [open, setOpen] = React.useState(false)

  const handleUnselect = (option: Option) => {
    onChange(selected.filter((s) => s.value !== option.value))
  }

  const handleSelect = (value: string) => {
    const option = options.find((opt) => opt.value === value)
    if (!option) return

    if (selected.some((s) => s.value === value)) {
      onChange(selected.filter((s) => s.value !== value))
    } else {
      onChange([...selected, option])
    }
  }

  // Make sure we're not trying to iterate over undefined
  const safeOptions = options || []
  const safeSelected = selected || []

  const selectables = safeOptions.filter((option) => !safeSelected.some((s) => s.value === option.value))

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <div className="flex min-h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-within:ring-2 focus-within:ring-ring focus-within:ring-offset-2">
          <div className="flex flex-wrap gap-1">
            {safeSelected.map((option) => (
              <Badge key={option.value} variant="secondary" className="rounded-sm px-1 font-normal">
                {option.label}
                <button
                  type="button"
                  className="ml-1 ring-offset-background rounded-full outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
                  onClick={(e) => {
                    e.preventDefault()
                    e.stopPropagation()
                    handleUnselect(option)
                  }}
                >
                  <X className="h-3 w-3 text-muted-foreground hover:text-foreground" />
                </button>
              </Badge>
            ))}
            <button
              type="button"
              onClick={() => setOpen(true)}
              className="bg-transparent px-2 text-sm text-muted-foreground"
            >
              {safeSelected.length === 0 ? placeholder : ""}
            </button>
          </div>
        </div>
      </PopoverTrigger>
      <PopoverContent className="w-full p-0" align="start">
        <Command>
          <CommandGroup className="max-h-[200px] overflow-auto">
            {selectables.length > 0 ? (
              selectables.map((option) => (
                <CommandItem key={option.value} value={option.value} onSelect={() => handleSelect(option.value)}>
                  {option.label}
                </CommandItem>
              ))
            ) : (
              <CommandItem disabled>No options available</CommandItem>
            )}
          </CommandGroup>
        </Command>
      </PopoverContent>
    </Popover>
  )
}
