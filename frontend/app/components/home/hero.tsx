import Container from '@/components/shared/container';
// Remove the direct SVG import
// import OysterIcon from '@/../public/oyster.svg'; 
import {
    Tabs,
    TabsContent,
    TabsList,
    TabsTrigger,
} from '@/components/ui/tabs';

// Remove font family arrays and helper function
// const fontSans = [...];
// const fontHeading = [...];

// Props interface currently empty, update if needed for future enhancements.
type Props = {};

export default function Hero({ }: Props) {
    return (
        <Container spacer={true}>
            {/* Main container using flexbox for vertical stacking */}
            <div className="flex flex-col items-center text-center py-16">

                {/* Crest Image */}
                <img
                    src="/b&p-crest.png"
                    alt="B&P Crest"
                    className="mb-4 h-48 w-auto" // Doubled height from h-24 to h-48
                />

                {/* Main Heading: RNSMiles font via h1 base styles, responsive size */}
                <h1 className="text-8xl text-[var(--accent-red)] lg:text-7xl md:text-6xl sm:text-4xl"> {/* Slightly smaller base size */}
                    SEASIDE
                </h1>

                {/* Couple Names: Manrope font via body inheritance, responsive sizes */}
                <p className="text-base text-[var(--foreground)] mt-2 sm:text-sm">
                    with
                </p>
                <p className="text-xl text-[var(--foreground)] md:text-lg sm:text-base">
                    Bazel and Parker
                </p>

                {/* Icon: Displayed using img tag. Color needs separate handling if required. */}
                <img
                    src="/oyster.svg"
                    alt="Oyster Icon"
                    className="my-4 h-10 w-10" // Consider responsive size sm:h-8 sm:w-8 ?
                />

                {/* Celebratory Message: Manrope font via body inheritance, responsive size */}
                <p className="text-base text-[var(--foreground)] sm:text-sm">
                    Join us as we celebrate our marriage
                </p>

                {/* Separator: Styled hr element */}
                <hr className="my-6 w-1/5 border-[var(--accent-red)] border-t-2" />

                {/*
                  Date & Location: RNSMiles font applied via font-heading class.
                  Year is intentionally omitted per PRD (TBD).
                  Confirm if font-heading class exists/is correct way to apply RNSMiles here.
                */}
                <p className="font-heading text-lg text-[var(--accent-red)] mt-4 md:text-base sm:text-sm">
                    MAY 8TH | SEASIDE, FLORIDA
                </p>

                {/* New Tabs Section for Daily Schedule */}
                <div className="w-full max-w-2xl mt-12"> {/* Added wrapper for tabs */}
                    <Tabs defaultValue="wed" className="w-full">
                        <TabsList className="grid w-full grid-cols-5">
                            <TabsTrigger value="wed">Wednesday</TabsTrigger>
                            <TabsTrigger value="thu">Thursday</TabsTrigger>
                            <TabsTrigger value="fri">Friday</TabsTrigger>
                            <TabsTrigger value="sat">Saturday</TabsTrigger>
                            <TabsTrigger value="sun">Sunday</TabsTrigger>
                        </TabsList>
                        <TabsContent value="wed" className="mt-4 text-left space-y-2">
                            <p><strong>1:00 PM:</strong> Welcome Drinks at Bud & Alley's</p>
                            <p><strong>3:00 PM:</strong> Beach Setup & Relaxation</p>
                            <p><strong>7:00 PM:</strong> Casual Dinner at The Great Southern Cafe</p>
                        </TabsContent>
                        <TabsContent value="thu" className="mt-4 text-left space-y-2">
                            <p><strong>9:00 AM:</strong> Optional Morning Yoga on the Beach</p>
                            <p><strong>11:00 AM:</strong> Group Bike Ride through Seaside</p>
                            <p><strong>1:00 PM:</strong> Lunch at The Meltdown on 30A (Airstream Row)</p>
                            <p><strong>6:00 PM:</strong> Rehearsal Dinner at Surfing Deer (Invite Only)</p>
                        </TabsContent>
                        <TabsContent value="fri" className="mt-4 text-left space-y-2">
                            <p><strong>Daytime:</strong> Relax & Explore Seaside!</p>
                            <p><strong>4:00 PM:</strong> Wedding Ceremony at Seaside Chapel</p>
                            <p><strong>5:00 PM:</strong> Cocktail Hour on the Lyceum Lawn</p>
                            <p><strong>6:30 PM:</strong> Reception Dinner & Dancing</p>
                        </TabsContent>
                        <TabsContent value="sat" className="mt-4 text-left space-y-2">
                            <p><strong>10:00 AM:</strong> Farewell Brunch at Fish Out of Water</p>
                            <p><strong>12:00 PM:</strong> Beach Day & Hangout</p>
                            <p><strong>7:00 PM:</strong> Sunset Cocktails at The Rooftop Bar</p>
                        </TabsContent>
                        <TabsContent value="sun" className="mt-4 text-left space-y-2">
                            <p><strong>Morning:</strong> Guests Depart</p>
                            <p><strong>11:00 AM:</strong> Last Chance Coffee at Amavida</p>
                            <p><strong>1:00 PM:</strong> Chill Afternoon at Grayton Beach State Park</p>
                        </TabsContent>
                    </Tabs>
                </div>

                {/* New Activities Section */}
                <div className="w-full max-w-2xl mt-16"> {/* Added wrapper for activities */}
                    <h2 className="font-heading text-4xl text-[var(--accent-red)] md:text-3xl sm:text-2xl mb-6">
                        ACTIVITIES
                    </h2>
                    <ul className="text-base text-[var(--foreground)] space-y-2">
                        <li>Spa</li>
                        <li>Beach Club</li>
                        <li>Shopping</li>
                        <li>Seaside Dining</li>
                        <li>Pickle Ball</li>
                    </ul>
                </div>
            </div>
        </Container>
    );
}

// Removed helper function
// function getFontClass(...) { ... }