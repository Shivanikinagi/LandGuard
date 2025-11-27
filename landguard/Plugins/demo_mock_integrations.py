"""
LandGuard Phase 11: Complete Demo with Mock Data
Works without any external APIs - uses sample data
"""

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from rich.progress import track
import time

from integrations.registry import IntegrationRegistry
from integrations.government.land_registry_mock import MockLandRegistryIntegration
from integrations.kyc.identity_verification_mock import MockIdentityVerificationIntegration
from integrations.valuation.property_valuation_mock import MockPropertyValuationIntegration


console = Console()


def print_header(title: str, emoji: str = "🎯"):
    """Print section header"""
    console.print(f"\n{'='*70}")
    console.print(f"[bold cyan]{emoji} {title}[/bold cyan]")
    console.print(f"{'='*70}\n")


def setup_mock_integrations() -> IntegrationRegistry:
    """Set up mock integrations"""
    print_header("Setting Up Mock Integrations", "🔧")
    
    registry = IntegrationRegistry()
    
    console.print("[cyan]Registering integrations with sample data...[/cyan]\n")
    
    # Register mock integrations with exact names
    steps = [
        ("land_registry", "Land Registry", MockLandRegistryIntegration),
        ("kyc", "KYC Service", MockIdentityVerificationIntegration),
        ("valuation", "Property Valuation", MockPropertyValuationIntegration)
    ]
    
    for registry_name, display_name, IntegrationClass in track(steps, description="Setting up..."):
        integration = IntegrationClass()
        registry.register(registry_name, integration, auto_enable=True)
        time.sleep(0.3)  # Dramatic effect
    
    console.print("\n[green]✅ All mock integrations ready![/green]")
    
    return registry


def demo_land_registry(registry: IntegrationRegistry):
    """Demo land registry with mock data"""
    print_header("Land Registry Demo", "🏛️")
    
    land_reg = registry.get('land_registry')
    
    # Test 1: Property Details
    console.print("[yellow]📋 Test 1: Fetching Property Details[/yellow]")
    console.print("[dim]Survey: 123/4, District: Mumbai, State: Maharashtra[/dim]\n")
    
    result = land_reg.get_property_details(
        survey_number="123/4",
        district="Mumbai",
        state="Maharashtra"
    )
    
    data = result['data']
    
    table = Table(title="Property Information", box=box.ROUNDED, show_header=False)
    table.add_column("Field", style="cyan", width=20)
    table.add_column("Value", style="white")
    
    table.add_row("Survey Number", data['survey_number'])
    table.add_row("District", data['district'])
    table.add_row("Owner", data['current_owner'])
    table.add_row("Area", f"{data['area']} {data['area_unit']}")
    table.add_row("Property Type", data['property_type'])
    table.add_row("Market Value", f"₹{data['market_value']:,}")
    table.add_row("Owner Since", data['owner_since'])
    table.add_row("Encumbrances", str(len(data['encumbrances'])))
    
    console.print(table)
    
    # Test 2: Ownership History
    console.print("\n[yellow]📜 Test 2: Ownership History[/yellow]\n")
    
    history = land_reg.get_ownership_history("123/4", "Mumbai", "Maharashtra")
    
    history_table = Table(title="Ownership Chain", box=box.ROUNDED)
    history_table.add_column("Owner", style="cyan")
    history_table.add_column("From", style="green")
    history_table.add_column("To", style="red")
    history_table.add_column("Transaction", style="yellow")
    
    for record in history[:5]:  # Show first 5
        history_table.add_row(
            record['owner_name'],
            record['ownership_from'],
            record['ownership_to'],
            record['transaction_type']
        )
    
    console.print(history_table)
    
    # Test 3: Encumbrances
    console.print("\n[yellow]🔒 Test 3: Encumbrance Check[/yellow]\n")
    
    enc_result = land_reg.check_encumbrances("123/4", "Mumbai", "Maharashtra")
    
    if enc_result['has_encumbrances']:
        console.print(f"[red]⚠️  Found {enc_result['count']} encumbrance(s)[/red]")
        for enc in enc_result['encumbrances']:
            console.print(f"  • {enc['type']}: ₹{enc['amount']:,} from {enc['creditor']}")
    else:
        console.print("[green]✅ No encumbrances found - Property is clear![/green]")


def demo_kyc_verification(registry: IntegrationRegistry):
    """Demo KYC with mock data"""
    print_header("KYC Verification Demo", "🔐")
    
    kyc = registry.get('kyc')
    
    # Test 1: Aadhar Verification
    console.print("[yellow]🆔 Test 1: Aadhar Verification[/yellow]\n")
    
    aadhar_result = kyc.verify_aadhar(
        aadhar_number="123456789012",
        name="Rajesh Kumar",
        consent=True
    )
    
    panel = Panel(
        f"""[cyan]Verified:[/cyan] {'✅ Yes' if aadhar_result['verified'] else '❌ No'}
[cyan]Name:[/cyan] {aadhar_result['name']}
[cyan]DOB:[/cyan] {aadhar_result['date_of_birth']}
[cyan]Gender:[/cyan] {aadhar_result['gender']}
[cyan]Address:[/cyan] {aadhar_result['address']}
[cyan]Masked Aadhar:[/cyan] {aadhar_result['masked_aadhar']}
[cyan]Confidence:[/cyan] {aadhar_result['confidence_score']}%""",
        title="[bold green]Aadhar Verification Result[/bold green]",
        border_style="green"
    )
    console.print(panel)
    
    # Test 2: PAN Verification
    console.print("\n[yellow]💳 Test 2: PAN Card Verification[/yellow]\n")
    
    pan_result = kyc.verify_pan(
        pan_number="ABCDE1234F",
        name="Rajesh Kumar"
    )
    
    table = Table(box=box.SIMPLE)
    table.add_column("Field", style="cyan")
    table.add_column("Value", style="white")
    
    table.add_row("Verified", "✅ Yes" if pan_result['verified'] else "❌ No")
    table.add_row("Name", pan_result['name'])
    table.add_row("PAN Number", pan_result['pan_number'])
    table.add_row("Status", pan_result['status'])
    table.add_row("DOB", pan_result['date_of_birth'])
    
    console.print(table)
    
    # Test 3: Comprehensive KYC
    console.print("\n[yellow]📊 Test 3: Comprehensive KYC Check[/yellow]\n")
    
    kyc_result = kyc.comprehensive_kyc(
        name="Rajesh Kumar",
        date_of_birth="1985-05-15",
        aadhar_number="123456789012",
        pan_number="ABCDE1234F",
        address="123 Main St, Mumbai"
    )
    
    status_color = "green" if kyc_result['kyc_status'] == 'approved' else "yellow"
    console.print(f"[{status_color}]KYC Status: {kyc_result['kyc_status'].upper()}[/{status_color}]")
    console.print(f"[cyan]Risk Score:[/cyan] {kyc_result['risk_score']}/100")
    console.print(f"[cyan]KYC ID:[/cyan] {kyc_result['kyc_id']}")
    
    console.print("\n[dim]Verifications:[/dim]")
    for check, passed in kyc_result['verifications'].items():
        status = "✅" if passed else "❌"
        console.print(f"  {status} {check}")


def demo_property_valuation(registry: IntegrationRegistry):
    """Demo property valuation with mock data"""
    print_header("Property Valuation Demo", "💰")
    
    valuation = registry.get('valuation')
    
    # Test 1: Value Estimation
    console.print("[yellow]💵 Test 1: Property Value Estimation[/yellow]\n")
    
    estimate = valuation.estimate_value(
        address="123 Main Street, Mumbai, Maharashtra",
        area_sqft=1500,
        property_type="residential",
        bedrooms=3,
        bathrooms=2
    )
    
    panel = Panel(
        f"""[cyan]Estimated Value:[/cyan] ₹{estimate['estimated_value']:,}
[cyan]Price per sqft:[/cyan] ₹{estimate['price_per_sqft']:,}
[cyan]Value Range:[/cyan] ₹{estimate['value_range']['low']:,} - ₹{estimate['value_range']['high']:,}
[cyan]Confidence:[/cyan] {estimate['confidence_score']}%
[cyan]Methodology:[/cyan] {estimate['methodology']}

[dim]Factors:[/dim]
  • Location Score: {estimate['factors']['location_score']}/10
  • Market Trend: {estimate['factors']['market_trend']}
  • Amenities Score: {estimate['factors']['amenities_score']}/10""",
        title="[bold green]Valuation Estimate[/bold green]",
        border_style="green"
    )
    console.print(panel)
    
    # Test 2: Comparable Sales
    console.print("\n[yellow]🏘️  Test 2: Comparable Sales Analysis[/yellow]\n")
    
    comparables = valuation.get_comparable_sales(
        address="123 Main Street, Mumbai",
        radius_km=2.0,
        max_results=5
    )
    
    comp_table = Table(title=f"Found {len(comparables)} Comparable Properties", box=box.ROUNDED)
    comp_table.add_column("Address", style="cyan", width=30)
    comp_table.add_column("Distance", justify="right")
    comp_table.add_column("Sale Price", justify="right", style="green")
    comp_table.add_column("Price/sqft", justify="right")
    comp_table.add_column("Similarity", justify="center")
    
    for comp in comparables[:5]:
        comp_table.add_row(
            comp['address'][:30],
            f"{comp['distance_km']} km",
            f"₹{comp['sale_price']:,}",
            f"₹{comp['price_per_sqft']:,}",
            f"{comp['similarity_score']}%"
        )
    
    console.print(comp_table)
    
    # Test 3: Market Trends
    console.print("\n[yellow]📈 Test 3: Market Trends[/yellow]\n")
    
    trends = valuation.get_market_trends(
        location="Mumbai",
        property_type="residential"
    )
    
    console.print(f"[cyan]Average Price:[/cyan] ₹{trends['average_price']:,}")
    console.print(f"[cyan]Median Price:[/cyan] ₹{trends['median_price']:,}")
    console.print(f"[cyan]Price Trend:[/cyan] {trends['price_trend'].upper()}")
    console.print(f"[cyan]YoY Change:[/cyan] {trends['yoy_change_percent']:+.2f}%")
    console.print(f"[cyan]MoM Change:[/cyan] {trends['mom_change_percent']:+.2f}%")
    console.print(f"[cyan]Inventory:[/cyan] {trends['inventory_level']}")
    
    # Test 4: Investment Analysis
    console.print("\n[yellow]📊 Test 4: Investment Analysis[/yellow]\n")
    
    investment = valuation.investment_analysis(
        purchase_price=5000000,
        address="123 Main Street, Mumbai",
        rental_income_monthly=35000,
        expected_appreciation_percent=8.0,
        holding_period_years=5
    )
    
    inv_table = Table(box=box.DOUBLE, title="Investment Metrics")
    inv_table.add_column("Metric", style="cyan")
    inv_table.add_column("Value", style="green", justify="right")
    
    inv_table.add_row("ROI", f"{investment['roi_percent']}%")
    inv_table.add_row("Cap Rate", f"{investment['cap_rate']}%")
    inv_table.add_row("Projected Value", f"₹{investment['projected_value']:,}")
    inv_table.add_row("Total Return", f"₹{investment['total_return']:,}")
    inv_table.add_row("Annual Return", f"{investment['annual_return_percent']}%")
    inv_table.add_row("Investment Grade", investment['investment_grade'])
    inv_table.add_row("Risk Score", f"{investment['risk_score']}/100")
    
    console.print(inv_table)


def show_statistics(registry: IntegrationRegistry):
    """Show integration statistics"""
    print_header("Integration Statistics", "📊")
    
    stats = registry.get_statistics()
    
    # Overall stats
    table1 = Table(title="Overall Statistics", box=box.DOUBLE)
    table1.add_column("Metric", style="cyan", width=25)
    table1.add_column("Value", style="bold yellow", justify="right")
    
    table1.add_row("Total Integrations", str(stats['total_integrations']))
    table1.add_row("Active Integrations", str(stats['active_integrations']))
    table1.add_row("Total Requests", str(stats['total_requests']))
    table1.add_row("Successful Requests", str(stats['successful_requests']))
    table1.add_row("Success Rate", f"{stats['success_rate']:.1f}%")
    
    console.print(table1)
    
    # Individual integration stats
    console.print("\n[cyan]Per-Integration Statistics:[/cyan]\n")
    
    table2 = Table(box=box.ROUNDED)
    table2.add_column("Integration", style="cyan")
    table2.add_column("Status", style="bold")
    table2.add_column("Requests", justify="right")
    table2.add_column("Success", justify="right")
    
    for name, integration in registry.integrations.items():
        info = integration.get_stats()
        table2.add_row(
            info['name'],
            f"✅ {info['status']}",
            str(info['statistics']['total_requests']),
            str(info['statistics']['successful_requests'])
        )
    
    console.print(table2)


def main():
    """Main demo function"""
    console.print(f"\n[bold magenta] {"="*70}[/bold magenta]")
    console.print("🎉 LandGuard Phase 11: Mock Integration Demo")
    console.print("   (Works without external APIs - uses sample data)")
    console.print(f"[bold magenta]{"="*70} [/bold magenta]")
    
    try:
        # Setup
        registry = setup_mock_integrations()
        
        # Run demos
        demo_land_registry(registry)
        demo_kyc_verification(registry)
        demo_property_valuation(registry)
        
        # Show statistics
        show_statistics(registry)
        
        # Final message
        print_header("Demo Complete", "🎊")
        
        panel = Panel(
            """[bold green]✅ All integrations working perfectly with mock data![/bold green]

[yellow]What you can do now:[/yellow]
  1. Explore the code to see how integrations work
  2. Modify mock data in integrations/mock_data.py
  3. Replace mock integrations with real APIs when ready
  4. Integrate with your fraud detection analyzer
  5. Build additional integrations using the same pattern

[cyan]Key Files:[/cyan]
  • integrations/mock_data.py - Sample data provider
  • integrations/government/land_registry_mock.py - Mock land registry
  • integrations/kyc/identity_verification_mock.py - Mock KYC
  • integrations/valuation/property_valuation_mock.py - Mock valuation

[dim]All data is randomly generated and consistent for testing.[/dim]""",
            title="[bold cyan]Success![/bold cyan]",
            border_style="cyan"
        )
        console.print(panel)
        
        # Cleanup
        registry.close_all()
        
    except KeyboardInterrupt:
        console.print("\n\n[yellow]Demo interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"\n[red]❌ Error: {e}[/red]")
        import traceback
        console.print(traceback.format_exc())
    
    console.print()


if __name__ == "__main__":
    main()