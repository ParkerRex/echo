import { useState } from "react";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { ThumbsUp, Edit2, Check, Sparkles, RefreshCw } from "lucide-react";
import { cn } from "@/lib/utils";

export type TitleOption = {
  id: string;
  text: string;
  votes?: number;
  isSelected?: boolean;
};

type TitleSelectorProps = {
  videoId: string;
  titleOptions: TitleOption[];
  onSelect: (titleId: string) => void;
  onEdit: (titleId: string, newText: string) => void;
  onVote: (titleId: string) => void;
  onGenerateMore: () => void;
  onApply: (titleId: string) => void;
  className?: string;
  maxDisplayedOptions?: number;
};

export function TitleSelector({
  videoId,
  titleOptions,
  onSelect,
  onEdit,
  onVote,
  onGenerateMore,
  onApply,
  className,
  maxDisplayedOptions = 5,
}: TitleSelectorProps) {
  const [editingTitleId, setEditingTitleId] = useState<string | null>(null);
  const [editText, setEditText] = useState("");
  const [showAllOptions, setShowAllOptions] = useState(false);

  const sortedOptions = [...titleOptions].sort((a, b) => (b.votes || 0) - (a.votes || 0));
  
  const displayedOptions = showAllOptions 
    ? sortedOptions 
    : sortedOptions.slice(0, maxDisplayedOptions);
  
  const selectedTitle = sortedOptions.find(title => title.isSelected);

  const handleEditStart = (title: TitleOption) => {
    setEditingTitleId(title.id);
    setEditText(title.text);
  };

  const handleEditSave = () => {
    if (editingTitleId && editText.trim()) {
      onEdit(editingTitleId, editText.trim());
      setEditingTitleId(null);
    }
  };

  const handleEditCancel = () => {
    setEditingTitleId(null);
  };

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle className="flex justify-between items-center">
          <span>Video Title Options</span>
          <Button 
            size="sm" 
            variant="outline" 
            onClick={onGenerateMore}
            className="gap-1"
          >
            <Sparkles className="h-3.5 w-3.5" />
            Generate More
          </Button>
        </CardTitle>
        <CardDescription>
          Select the best title for your video or create your own
        </CardDescription>
      </CardHeader>
      
      <CardContent className="space-y-4">
        {/* Selected Title Preview */}
        {selectedTitle && (
          <div className="p-3 border rounded-md bg-muted/50">
            <div className="text-xs text-muted-foreground mb-1">Selected Title</div>
            <div className="font-medium">{selectedTitle.text}</div>
          </div>
        )}
        
        {/* Title Options */}
        <div className="space-y-3">
          {displayedOptions.map((title) => (
            <div 
              key={title.id}
              className={cn(
                "p-3 border rounded-md relative transition",
                title.isSelected 
                  ? "border-primary/50 bg-primary/5" 
                  : "hover:border-border/80"
              )}
            >
              {editingTitleId === title.id ? (
                <div className="space-y-2">
                  <Input
                    value={editText}
                    onChange={(e) => setEditText(e.target.value)}
                    className="w-full"
                    autoFocus
                  />
                  <div className="flex space-x-2 justify-end">
                    <Button 
                      size="sm" 
                      variant="ghost" 
                      onClick={handleEditCancel}
                    >
                      Cancel
                    </Button>
                    <Button 
                      size="sm" 
                      onClick={handleEditSave}
                    >
                      Save
                    </Button>
                  </div>
                </div>
              ) : (
                <>
                  <div className="mr-16 text-sm">{title.text}</div>
                  <div className="absolute right-3 top-3 flex items-center space-x-2">
                    <Button 
                      size="icon" 
                      variant="ghost" 
                      className="h-7 w-7"
                      onClick={() => onVote(title.id)}
                    >
                      <ThumbsUp className="h-3.5 w-3.5" />
                      {title.votes && title.votes > 0 && (
                        <span className="absolute -top-0.5 -right-0.5 bg-primary text-[10px] text-primary-foreground w-4 h-4 flex items-center justify-center rounded-full">
                          {title.votes}
                        </span>
                      )}
                    </Button>
                    <Button 
                      size="icon" 
                      variant="ghost" 
                      className="h-7 w-7"
                      onClick={() => handleEditStart(title)}
                    >
                      <Edit2 className="h-3.5 w-3.5" />
                    </Button>
                    <Button 
                      size="icon" 
                      variant="ghost" 
                      className={cn(
                        "h-7 w-7", 
                        title.isSelected && "text-primary"
                      )}
                      onClick={() => onSelect(title.id)}
                    >
                      <Check className="h-3.5 w-3.5" />
                    </Button>
                  </div>
                </>
              )}
            </div>
          ))}
          
          {titleOptions.length > maxDisplayedOptions && (
            <Button
              variant="ghost"
              size="sm"
              className="w-full text-xs"
              onClick={() => setShowAllOptions(!showAllOptions)}
            >
              {showAllOptions ? "Show Less" : `Show ${titleOptions.length - maxDisplayedOptions} More Options`}
            </Button>
          )}
        </div>
      </CardContent>
      
      <CardFooter>
        <Button 
          className="w-full"
          disabled={!selectedTitle}
          onClick={() => selectedTitle && onApply(selectedTitle.id)}
        >
          Apply Selected Title
        </Button>
      </CardFooter>
    </Card>
  );
}