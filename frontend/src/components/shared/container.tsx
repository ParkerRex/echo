import { cn } from '@/lib/utils';

type Props = {
    children: React.ReactNode;
    tag?: 'div' | 'section' | 'header' | 'footer';
    className?: string;
    id?: string;
    spacer?: boolean;
    padding?: boolean;
};

export default function Container({
    children,
    tag = 'div',
    className,
    id,
    spacer = false,
    padding = true,
}: Props) {
    const Tag = tag;
    return (
        <Tag
            className={cn(
                'w-full flex flex-col',
                spacer ? 'mt-19' : '',
                padding ? 'px-6 md:px-8 lg:px-10' : '',
                className,
            )}
            id={id}
        >
            {children}
        </Tag>
    );
}